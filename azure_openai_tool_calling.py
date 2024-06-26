import json
import logging
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from tenacity import retry, stop_after_attempt, wait_random_exponential
from termcolor import colored

from tools import available_functions, tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globals
# Your deployment name with a model supporting tools (version 1106 at minimum)
GPT_MODEL = "gpt_turbo"
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_ad_token_provider=token_provider,
)

TOOL_CALL_SYSTEM_MESSAGE = "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."


class Conversation:
    """Class to track the conversation history and display the chat in human readable form."""

    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.history.append(message)

    def pretty_print_conversation(self):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }

        for message in self.history:
            # Convert Pydantic models to dict for consistent behavior
            if isinstance(message, ChatCompletionMessage):
                message = message.dict()

            if message["role"] == "system":
                print(colored(f"System: {message['content']}", role_to_color[message["role"]]))
            elif message["role"] == "user":
                print(colored(f"User: {message['content']}", role_to_color[message["role"]]))
            elif message["role"] == "assistant" and message.get("tool_calls"):
                for tool_call in message.get("tool_calls"):
                    function = tool_call["function"]
                    print(
                        colored(
                            f"Assistant: Call function `{function['name']}` with arguments: {function['arguments']}",
                            role_to_color[message["role"]],
                        )
                    )
            elif message["role"] == "assistant" and not message.get("tool_calls"):
                print(colored(f"Assistant: {message['content']}", role_to_color[message["role"]]))
            elif message["role"] == "function":
                print(
                    colored(
                        f"Function `{message['name']}` returns: {message['content']}",
                        role_to_color[message["role"]],
                    )
                )


def chat(messages: list[dict], tools=None) -> ChatCompletionMessage:
    chat_response = chat_completion_request(messages, tools=tools)

    # Assistant message
    choice = chat_response.choices[0]

    # Check if a tool call is required
    if choice.finish_reason == "tool_calls":
        logger.info("Tool call requested, calling function")
        function_message = handle_tool_call(choice.message)
        messages.append(function_message)

        # Create a new response that used the function call
        # Set tools=None to avoid doing another tool call.
        chat_response = chat_completion_request(messages, tools=None)

    return chat_response


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as exc:
        logger.error("Unable to generate ChatCompletion response.")
        logger.error("Exception: %s", exc)
        return exc


def handle_tool_call(message: ChatCompletionMessage):
    """NOTE for now not parallel, only does the first tool call"""
    # Do nothing if no tool calls are asked for
    if not message.tool_calls:
        return

    # TODO handle multiple tool calls `for tool_call in tool_calls`
    try:
        tool_call: ChatCompletionMessageToolCall = message.tool_calls[0]
        function_name = tool_call.function.name
        tool_call_id = tool_call.id
        arguments = json.loads(tool_call.function.arguments)

        callable_function = available_functions[function_name]
        function_result = callable_function(**arguments)

        function_message = {
            "role": "function",
            "tool_call_id": tool_call_id,
            "name": function_name,
            "content": function_result,
        }
        return function_message

    except KeyError:
        logger.error("Tool call is not available.")


def run_conversation(user_query: str, tools=None):
    conversation = Conversation()
    conversation.add_message("system", TOOL_CALL_SYSTEM_MESSAGE)

    # User query
    conversation.add_message("user", user_query)
    chat_response = chat(conversation.history, tools=tools)

    # Answer of the assistant, including tool call
    assistant_message = chat_response.choices[0].message.content
    conversation.add_message("assistant", assistant_message)

    # Detailed inspection of all completion objects
    print("All completions:\n----------------")
    for message in conversation.history:
        print(message)
    print()

    # A human readable printout of the conversation
    conversation.pretty_print_conversation()


if __name__ == "__main__":
    # For this weather query, a tool call is available
    run_conversation("What's the weather like today in Nijmegen, Netherlands?", tools=tools)

    # As a weather question about a place where Fahrenheit is used
    # run_conversation("What's the weather like today in George Town, Cayman Islands?", tools=tools)
    run_conversation("What's the weather like today in New York, United States?", tools=tools)

    # This query is completely unrelated, but we pass tools anyways
    run_conversation("Tell me something interesting", tools=tools)

    # This query is completely unrelated and we do not pass tools
    run_conversation("Tell me something interesting", tools=None)

    # Related to the train disruptions call
    run_conversation("Zijn er momenteel treinstoringen?", tools=tools)

    # Ask about disruptions on a specific train station
    run_conversation("Zijn er momenteel treinstoringen rondom station Amsterdam?", tools=tools)
    run_conversation("Zijn er momenteel treinstoringen rondom station Nijmegen?", tools=tools)
    run_conversation("Zijn er momenteel treinstoringen rondom station Rotterdam?", tools=tools)
