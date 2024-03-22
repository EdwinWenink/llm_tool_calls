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

This uses a dummy `get_current_weather` function that always says it's 20 degrees.
The main point here is that LLM knows how to fill the `location` and `format` parameters from the user query and use these in the function call:

```
System: Don't make assumptions about what values to plug into functions.
    Ask for clarification if a user request is ambiguous.

User: What's the weather like today in Nijmegen, Netherlands?

Function `get_current_weather` returns: It's 20 degrees celsius in Nijmegen, Netherlands

Assistant: The current temperature in Nijmegen, Netherlands is 20 degrees Celsius.
    If you need more detailed weather information, feel free to ask!
```

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
