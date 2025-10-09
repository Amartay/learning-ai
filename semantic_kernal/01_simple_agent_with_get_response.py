import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread

async def main():
    # Initialize a chat agent with basic instructions
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="SK-Assistant",
        instructions="You are a helpful assistant.",
    )

    # Get a response to a user message
    # response = await agent.get_response(messages="Write a haiku about Semantic Kernel.")
    # print(response.content)

    thread: ChatHistoryAgentThread | None = None

    user_inputs = [
        "Plan me a day trip.",
    ]

    for user_input in user_inputs:
        print(f"# User: {user_input}\n")
        first_chunk = True
        async for response in agent.invoke_stream(
            messages=user_input, thread=thread,
        ):
            # 5. Print the response
            if first_chunk:
                print(f"# {response.name}: ", end="", flush=True)
                first_chunk = False
            print(f"{response}", end="", flush=True)
            thread = response.thread
        print()

    # Clean up the thread
    await thread.delete() if thread else None

asyncio.run(main()) 

# Output:
# Language's essence,
# Semantic threads intertwine,
# Meaning's core revealed.
