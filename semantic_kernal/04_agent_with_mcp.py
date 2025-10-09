# Import cell - Updated imports
import json
import os
import asyncio

from dotenv import load_dotenv
from IPython.display import display, HTML
from typing import Annotated

from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.contents import FunctionCallContent, FunctionResultContent, StreamingTextContent

# Main execution cell - Enhanced with proper HTML rendering and MCP tool logging
# User requests for Airbnb search
user_inputs = [
    "Find Airbnb in Stockholm for 2 adults 1 kid",
]


async def main():
    """Main function to run the MCP-enabled agent with real OpenBnB server using Azure OpenAI"""

    try:
        # Create MCP plugin connection to real OpenBnB server
        async with MCPStdioPlugin(
            name="AirbnbSearch",
            description="Search for Airbnb accommodations using OpenBnB MCP server",
            command="npx",
            args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        ) as airbnb_plugin:

            print("🔧 MCP Plugin created and connected")

            # Load tools for function discovery
            await airbnb_plugin.load_tools()
            await asyncio.sleep(3)  # Give more time for initialization
            print("✅ Tools loaded from MCP server")

            # Debug: Check what tools were loaded
            if hasattr(airbnb_plugin, '_tools'):
                print(f"📋 Internal tools: {airbnb_plugin._tools}")

            # Verify available functions
            funcs = [attr for attr in dir(airbnb_plugin)
                     if callable(getattr(airbnb_plugin, attr))
                     and attr in ['airbnb_search', 'airbnb_listing_details']]
            print(f"📋 Available functions: {funcs}")

            # Create agent with Azure OpenAI service
            agent = ChatCompletionAgent(
                service=AzureChatCompletion(),  # Use default constructor
                name="AirbnbAgent",
                instructions="""You are an Airbnb search assistant. Use the airbnb_search function to find properties. 
                Format results in a clear HTML table with columns for property name, price, rating, and link.""",
                plugins=[airbnb_plugin],
            )

            print("🤖 Agent created with Azure OpenAI")

            # Process each user input
            thread: ChatHistoryAgentThread | None = None

            for user_input in user_inputs:
                print(f"\n🔍 Processing request: {user_input}")
                
                # Track MCP tool usage
                mcp_tools_used = []
                function_calls_log = []
                
                # Try streaming to capture function calls
                try:
                    agent_name = None
                    full_response = []
                    current_function_name = None
                    argument_buffer = ""
                    
                    async for response in agent.invoke_stream(
                        messages=user_input,
                        thread=thread,
                    ):
                        thread = response.thread
                        agent_name = response.name
                        
                        for item in response.items:
                            # Log function calls
                            if isinstance(item, FunctionCallContent):
                                if item.function_name:
                                    current_function_name = item.function_name
                                    mcp_tools_used.append(item.function_name)
                                    print(f"\n🔧 MCP Tool Selected: {item.function_name}")
                                    
                                if isinstance(item.arguments, str):
                                    argument_buffer += item.arguments
                            
                            # Log function results
                            elif isinstance(item, FunctionResultContent):
                                if current_function_name:
                                    try:
                                        args = json.loads(argument_buffer.strip()) if argument_buffer else {}
                                    except:
                                        args = {"raw": argument_buffer}
                                    
                                    function_calls_log.append({
                                        "function": current_function_name,
                                        "arguments": args,
                                        "timestamp": asyncio.get_event_loop().time()
                                    })
                                    
                                    print(f"   📍 Arguments: {json.dumps(args, indent=2)}")
                                    print(f"   ✅ MCP Tool Executed Successfully")
                                    
                                    current_function_name = None
                                    argument_buffer = ""
                            
                            # Collect response text
                            elif isinstance(item, StreamingTextContent) and item.text:
                                full_response.append(item.text)
                    
                    # Join the full response
                    response_text = ''.join(full_response)
                    
                except Exception as e:
                    print(f"⚠️ Streaming failed, using get_response: {str(e)[:100]}")
                    # Fallback to non-streaming
                    response = await agent.get_response(messages=user_input, thread=thread)
                    thread = response.thread
                    response_text = str(response)
                    agent_name = response.name
                
                
                # Process the response to ensure HTML tables render correctly
                # Remove any markdown code blocks around HTML
                response_text = response_text.replace('```html', '').replace('```', '')
                
                # Ensure proper HTML structure for tables
                if '<table' in response_text.lower():
                    # Add CSS styling for better table rendering
                    table_css = """
                    <style>
                        .airbnb-results table {
                            border-collapse: collapse;
                            width: 100%;
                            margin: 10px 0;
                        }
                        .airbnb-results th, .airbnb-results td {
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }
                        .airbnb-results th {
                            background-color: #f2f2f2;
                            font-weight: bold;
                        }
                        .airbnb-results tr:nth-child(even) {
                            background-color: #f9f9f9;
                        }
                        .airbnb-results a {
                            color: #1976d2;
                            text-decoration: none;
                        }
                        .airbnb-results a:hover {
                            text-decoration: underline;
                        }
                    </style>
                    """
                    response_text = f'{table_css}<div class="airbnb-results">{response_text}</div>'
                
                # Build the complete HTML output
                html_output = f"""
                <div style='margin:10px; padding:10px; border-left:3px solid #2E8B57; background:#F0F8FF;'>
                    <strong>User:</strong> {user_input}
                </div>
                """
                
                # Add function call details if available
                if function_calls_log:
                    details_html = "<details style='margin:10px; padding:10px; background:#f5f5f5;'>"
                    details_html += "<summary><strong>📊 Function Call Details</strong></summary>"
                    details_html += "<pre style='background:#fff; padding:10px; overflow-x:auto;'>"
                    for call in function_calls_log:
                        details_html += f"Function: {call['function']}\n"
                        details_html += f"Arguments: {json.dumps(call['arguments'], indent=2)}\n"
                        details_html += "---\n"
                    details_html += "</pre></details>"
                    html_output += details_html
                
                # Add the agent's response with proper HTML rendering
                html_output += f"""
                <div style='margin:10px; padding:15px; border-left:3px solid #1E90FF; background:#FFFFFF;'>
                    <strong>{agent_name}:</strong><br>
                    {response_text}
                </div>
                """
                
                # Display the HTML with proper rendering
                display(HTML(html_output))
                
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

print("🚀 Starting with Azure OpenAI...")
asyncio.run(main())
print("✅ Done!")