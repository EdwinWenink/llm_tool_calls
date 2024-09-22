from conversation import run_conversation
from tools import tools

# TODO validate arguments of a function call
"""
import inspect

# helper method used to check if the correct arguments are provided to a function
def check_args(function, args):
    sig = inspect.signature(function)
    params = sig.parameters

    # Check if there are extra arguments
    for name in args:
        if name not in params:
            return False
    # Check if the required arguments are provided
    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False

    return True
"""

if __name__ == "__main__":
    """
    # For this weather query, a tool call is available
    run_conversation("What's the weather like today in Nijmegen, Netherlands?", tools=tools)

    # As a weather question about a place where Fahrenheit is used
    # run_conversation("What's the weather like today in George Town, Cayman Islands?", tools=tools)
    run_conversation("What's the weather like today in New York, United States?", tools=tools)

    # This query is completely unrelated, but we pass tools anyways
    run_conversation("Tell me something interesting", tools=tools)

    # This query is completely unrelated and we do not pass tools
    run_conversation("Tell me something interesting", tools=None)
    """

    # Related to the train disruptions call
    # run_conversation("Zijn er momenteel treinstoringen?", tools=tools)
    run_conversation("Zijn er momenteel treinstoringen in Nederland?", tools=tools)

    # Ask about disruptions on a specific train station
    # run_conversation("Zijn er momenteel treinstoringen rondom station Amsterdam?", tools=tools)
    # run_conversation("Zijn er momenteel treinstoringen rondom station Nijmegen?", tools=tools)
    # run_conversation("Zijn er momenteel treinstoringen rondom station Rotterdam?", tools=tools)
    # run_conversation("Zijn er momenteel treinstoringen rondom station Best?", tools=tools)