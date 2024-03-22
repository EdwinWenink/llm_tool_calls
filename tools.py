"""
This module contains the available tool calls
"""


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        },
    },
]


def get_current_weather(location: str, format: str):
    return f"It's 20 degrees {format} in {location}"


# Dynamically generate mapping of available functions
# This assumes the function name in the tool call is identical to the function def
function_names = [tool["function"]["name"] for tool in tools]

available_functions = {function_name: globals()[function_name] for function_name in function_names}
