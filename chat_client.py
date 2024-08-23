import os
from abc import ABC, abstractmethod

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
)


# Make an abstract class called ChatClient that has a method called chat
# that takes a list of messages and returns a ChatCompletionMessage.
class ChatClient(ABC):
    @abstractmethod
    def create_completion(self, messages, tools=None, tool_choice=None):
        pass


class AzureOpenAIChatClient(ChatClient):
    """
    This client uses the AzureOpenAI SDK to directly talk with a deployment
    """
    def __init__(self, deployment_name: str):
        # Your deployment name with a model supporting tools (version 1106 at minimum)
        self.deployment_name = deployment_name  # "gpt_turbo"
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        API_VERSION = os.getenv("API_VERSION")
        AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
        assert AZURE_ENDPOINT, "Please set the AZURE_OPENAI_ENDPOINT environment variable."

        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
            azure_ad_token_provider=token_provider,
        )

    def create_completion(self, messages, tools=None, tool_choice=None) -> ChatCompletion:
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response




class RequestsClient(ChatClient):
    """
    This client uses a REST API to talk with a deployment.
    """
    pass