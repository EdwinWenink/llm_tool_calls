from conversation import run_conversation
from tools import tools

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
    # run_conversation("Zijn er momenteel treinstoringen in Nederland?", tools=tools)

    # run_conversation("Wie is Thomas Strikwerda?", tools=tools)
    # run_conversation("Wie is Edwin Wenink?", tools=tools)
    # run_conversation("Wie is Wenink, Edwin?", tools=tools)
    # run_conversation("Wie is Eric?", tools=tools)
    # run_conversation("Wie is Eric Paape?", tools=tools)
    # run_conversation("Wie is Hankie Pankie?", tools=tools)
    run_conversation("Wie is Leo van der Meulen?", tools=tools)

    # Team
    # run_conversation("Wat is team Knipteam?", tools=tools)
    # run_conversation("Wat is team DIA.SIMBA?", tools=tools)

    # Ask about disruptions on a specific train station
    # run_conversation("Zijn er momenteel treinstoringen rondom station Amsterdam?", tools=tools)
    # run_conversation("Zijn er momenteel treinstoringen rondom station Nijmegen?", tools=tools)
    # run_conversation("Zijn er momenteel treinstoringen rondom station Rotterdam?", tools=tools)
    # run_conversation("Zijn er momenteel treinstoringen rondom station Best?", tools=tools)
