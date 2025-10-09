import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread

# Example Native Plugin (Tool)
class WeatherPlugin:
    @kernel_function(name="get_weather", description="Gets the weather for a city")
    def get_weather(self, city: str) -> str:
        """Retrieves the weather for a given city."""
        if "paris" in city.lower():
            return f"The weather in {city} is 20°C and sunny."
        elif "london" in city.lower():
            return f"The weather in {city} is 15°C and cloudy."
        else:
            return f"Sorry, I don't have the weather for {city}."

import asyncio

async def main():
    # Setup Semantic Kernel
    kernel = sk.Kernel()

    # Add your AI service (e.g., Azure OpenAI)
    ai_service = AzureChatCompletion()
    kernel.add_service(ai_service)

    # Import the WeatherPlugin
    kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")

    agent = ChatCompletionAgent(
        kernel=kernel,
        name="Host",
        instructions="You are a helpful assistant",
    )

    # Create a thread to maintain conversation history
    thread = ChatHistoryAgentThread()

    print("Type 'exit' to end the conversation.")
    while True:
        user_msg = input("User: ")
        if user_msg.lower() == "exit":
            break
        response = await agent.get_response(messages=user_msg, thread=thread)
        print(f"Assistant: {response.content}\n")
        thread = response.thread

if __name__ == "__main__":
    asyncio.run(main())