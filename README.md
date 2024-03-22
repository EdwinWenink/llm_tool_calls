# LLM Tool Calls

Repository for experimenting with tool calls in LLMs (so far, GPTs hosted in Azure).
This demo does not use the deprecated `function_calls` but instead uses the newer `tool_calls`.

Authentication is done using AD token authorization, not with API keys.

## Environment variables

Set the following variables in `.env`:

```
AZURE_OPENAI_ENDPOINT=
API_VERSION=
```

Note that only more recent APIs have access to tool calling.


## Conversation about the weather

This uses a dummy `get_current_weather` function that does not actually call an API but always says it's 20 degrees.
The main point here is that LLM knows how to fill the `location` and `format` parameters from the user query and use these in the function call:

```
System: Don't make assumptions about what values to plug into functions.
    Ask for clarification if a user request is ambiguous.

User: What's the weather like today in Nijmegen, Netherlands?

Function `get_current_weather` returns: It's 20 degrees celsius in Nijmegen, Netherlands

Assistant: The current temperature in Nijmegen, Netherlands is 20 degrees Celsius.
    If you need more detailed weather information, feel free to ask!
```

The query does not specify whether to give the temperature in Celsius or Fahrenheit.
This is inferred from the location!
The description of the `format` parameter explicitly mentions that it should be inferred from the context.

Let's check if Fahrenheit is used when we ask about a city in the United States instead.
I changed the default answer to 60 degrees because this range is more plausible for Fahrenheit but very implausible for Celcius.
Too bad: the assistant still answers in Celcius, but amusingly does note that this is exceptionally hot:

```
System: Don't make assumptions about what values to plug into functions.
    Ask for clarification if a user request is ambiguous.

User: What's the weather like today in New York, United States?

Function `get_current_weather` returns: It's 60 degrees celsius in New York, United States

Assistant: It seems there might be a misunderstanding.
    The temperature you provided, 60 degrees Celsius, seems unusually high for the current weather in New York.
    Could you confirm if that is the correct temperature measurement?
```

The parameter description in the tool call is `"enum": ["celsius", "fahrenheit"]`.
If I switch the order around, the model instead starts using `Fahrenheit` in the answer.
It seems that if the model fails to infer the correct temperature format, it uses the first enum value by default.

## Queries without relevant function calls

When the user makes a query that is not related to any of the available tools, it should not call any tools.
In this particular instance, I did pass the available tools to let the LLM decide for itself whether to use the tool.

```
System: Don't make assumptions about what values to plug into functions.
    Ask for clarification if a user request is ambiguous.

User: Tell me something interesting

Assistant: Sure! Did you know that the city of San Francisco is known for its foggy weather?
    This fog is a result of the cool air from the Pacific Ocean meeting the warm air from inland areas,
    creating the iconic fog that often blankets the city. If you'd like, I can also provide you with the current weather in San Francisco. Just let me know!
```

Observations:

- Even though the LLM did not make a tool call (rightly so), the description of the weather function (which is about San Francisco) clearly biased the answer!
- It's also quite interesting that the assistant offers to look up the weather and makes known that it has the capability to do so.

Let's repeat the same query without passing any tools.
This gives a random interesting fact, like expected:

```
System: Don't make assumptions about what values to plug into functions.
    Ask for clarification if a user request is ambiguous.

User: Tell me something interesting

Assistant: Did you know that honey never spoils? Archaeologists have found pots of honey
    in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.
    The long shelf life of honey is due to its low moisture content and acidic pH,
    which create an inhospitable environment for bacteria and microorganisms.
```

## Train Disruptions API

Add `NS_APP_KEY` to `.env`.

The second tool queries an NS Disruptions API (you can make an account [here](https://apiportal.ns.nl/)) for current disruptions in train operations.

The following conversation was run on 22-03-2024 around 8:30 PM (in Dutch):

```
System: Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.

User: Zijn er momenteel treinstoringen?

Function `get_all_train_disruptions` returns: Groningen - Leer. werkzaamheden
    Amsterdam - Rotterdam - Breda. beperkingen materieel

Assistant: Er zijn momenteel twee treinstoringen:

1. Tussen Groningen en Leer zijn er werkzaamheden.
2. Op de route Amsterdam - Rotterdam - Breda zijn er beperkingen vanwege materieel.

Laat me weten als je nog meer informatie nodig hebt!
```

For reference, this was the overview of disruptions on ns.nl at the same time:

![03-2024-disruptions]( data/22-03-2024-disruptions.png )
