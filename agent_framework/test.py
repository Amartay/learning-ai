import asyncio
from agent_framework.observability import setup_observability
from agent_framework.observability import get_tracer, get_meter

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

setup_observability(
    enable_sensitive_data=True
)


tracer = get_tracer()
meter = get_meter()

with tracer.start_as_current_span("my_custom_span"):
    # Your code here
    pass

counter = meter.create_counter("my_custom_counter")
counter.add(1, {"key": "value"})


# Create the agent - telemetry is automatically enabled
agent = AzureOpenAIChatClient(credential=AzureCliCredential()).create_agent(
    instructions="You are good at telling jokes.",
    name="Joker"
)
# Run the agent
result = await agent.run("Tell me a joke about a pirate.")
print(result)