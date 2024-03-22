# LLM Tool Calls

Repository for experimenting with tool calls in LLMs (so far, GPTs hosted in Azure).

Authentication is done using AD token authorization, not with API keys.


## Conversation about the weather

This uses a dummy `get_current_weather` function:

```python
System: Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
User: What's the weather like today in Nijmegen, Netherlands?
Function `get_current_weather` returns: It's 20 degrees celsius in Nijmegen, Netherlands
Assistant: The current temperature in Nijmegen, Netherlands is 20 degrees Celsius. If you need more detailed weather information, feel free to ask!
```
