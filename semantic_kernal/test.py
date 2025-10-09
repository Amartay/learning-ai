import asyncio
import os
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.mcp import MCPStdioPlugin

# Make sure these environment variables are set:
#   AZURE_OPENAI_API_KEY
#   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
#   AZURE_OPENAI_ENDPOINT
#   GITHUB_TOKEN (Personal Access Token with repo read access)

USER_INPUTS = [
    "List all files in repository Amartay/Adobe",
]

async def main():
    token = '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'

    print(token)
    if not token:
        raise RuntimeError("Set GITHUB_TOKEN environment variable with your GitHub PAT")

    # Launch GitHub MCP server using npx
    async with MCPStdioPlugin(
        name="github",
        description="GitHub MCP Server",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_TOKEN": token}  # Pass token to MCP server
    ) as github_plugin:

        # Create Azure OpenAI chat completion service
        service = AzureChatCompletion()

        # Create the agent
        agent = ChatCompletionAgent(
            service=service,
            name="IssueAgent",
            instructions="Answer questions about GitHub repositories",
            plugins=[github_plugin]
        )

        thread: ChatHistoryAgentThread | None = None

        for user_input in USER_INPUTS:
            print(f"User: {user_input}")
            response = await agent.get_response(messages=user_input, thread=thread)
            print(f"{response.name}: {response}")
            thread = response.thread

        # Cleanup
        if thread:
            await thread.delete()

if __name__ == "__main__":
    asyncio.run(main())