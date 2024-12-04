"""
This module contains the available tool calls
"""

from request_train_disruptions import (request_disruptions_at_station,
                                       request_train_disruptions)
from team_centraal import find_team_member, get_team_info

_ = get_team_info

# TODO Pydantic model for 'tools'

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
    {
        "type": "function",
        "function": {
            "name": "get_all_train_disruptions",
            "description": "Get all current disruptions of trains in the Netherlands",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_disruptions_for_train_station",
            "description": "Get disruptions for a specific train station in the Netherlands",
            "parameters": {
                "type": "object",
                "properties": {
                    "station_code": {
                        "type": "string",
                        "description": "The official station code abbrevation, e.g. 'Nm' for station Nijmegen and 'Asd' for Amsterdam.",
                    }
                },
                "required": ["station_code"],
            },
        },
    },
    # Who is who functionality
    {
        "type": "function",
        "function": {
            "name": "get_team_member",
            "description": "Get information about who a person at the Nederlandse Spoorwegen (NS) is and to which team he or she belongs. Also describes the team and its skills and ambitions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Either the first or last name of the person to look up, but not both!.",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_info",
            "description": "Get information about a team at the Nederlandse Spoorwegen (NS), including its members, the applications they work on, and the department they belong to.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "The name of the team.",
                    }
                },
                "required": ["name"],
            },
        },
    },
]


def get_current_weather(location: str, format: str) -> str:
    return f"It's 20 degrees {format} in {location}"


def get_all_train_disruptions() -> str:
    return request_train_disruptions()


def get_disruptions_for_train_station(station_code: str) -> str:
    # NOTE at this point we could manually try to normalize station names to valid station codes.
    # For now, let's see if the LLM figures this out on its own.
    return request_disruptions_at_station(station_code)


def get_team_member(name: str) -> str:
    # TODO possibly do extra handling here in case there are multiple persons.
    return find_team_member(name)


# Dynamically generate mapping of available functions
# This assumes the function name in the tool call is identical to the function def
function_names = [tool["function"]["name"] for tool in tools]

available_functions = {
    function_name: globals()[function_name] for function_name in function_names
}
