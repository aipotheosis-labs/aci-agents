"""
Due to the limitation of the MCP protocol, when starting the Unified or Apps MCP server, you need to pass in the --linked-account-owner-id parameter.
This works for the case where there is only one user (e.g. the user who is running the MCP server).
However, for multi-user usecases (which is what our platform is designed for), we need a way to specify the linked_account_owner_id dynamically
depending on  who is the function execution for (e.g., when sending emails, which owner's linked gmail account should be used).

As a temporay solution, in the MCP server (both unified and apps), we allow user (MCP clients) to pass in the "linked_account_owner_id" parameter 
for the ACI_EXECUTE_FUNCTION tool call (apart from the "function_name" and "function_arguments" parameters).

You still need to pass in the --linked-account-owner-id flag when starting the MCP server. (e.g., uvx aci-mcp unified-mcp --linked-account-owner-id <owner_id>)
This value will be used as the default value of the "linked_account_owner_id" parameter, in case no override is provided for the ACI_EXECUTE_FUNCTION tool call.

Below is an MCP client example that showcases how to adapt to this temporary solution.

What's need to be done is basciaclly to intercept the ACI_EXECUTE_FUNCTION tool call and 
add the "linked_account_owner_id" parameter to the tool call arguments.
"""

from aci.meta_functions import ACIExecuteFunction
from dotenv import load_dotenv
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic


load_dotenv()

ACI_OVERRIDE_LINKED_ACCOUNT_OWNER_ID = <YOUR_LINKED_ACCOUNT_OWNER_ID_OVERRIDE>

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self):
        """Connect to an MCP server
        """
        server_params = StdioServerParameters(
            command="uvx",
            args=["aci-mcp", "unified-server", "--linked-account-owner-id", os.getenv("LINKED_ACCOUNT_OWNER_ID")],
            env={"ACI_API_KEY": os.getenv("ACI_API_KEY")}
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])


    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        messages = []

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]


        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                messages.append({
                    "role": "user",
                    "content": query
                })

                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                assistant_message_content = []
                for content in response.content:
                    if content.type == 'text':
                        print(content.text)
                        assistant_message_content.append({
                            "type": "text",
                            "text": content.text
                        })
                    elif content.type == 'tool_use':
                        tool_name = content.name
                        tool_args = content.input
                        assistant_message_content.append({
                            "type": "tool_use",
                            "id": content.id,
                            "name": tool_name,
                            "input": tool_args
                        })
                        # Execute tool call
                        print(f"[Calling tool {tool_name} with args {tool_args}]")
                        messages.append({
                            "role": "assistant",
                            "content": assistant_message_content
                        })

                        # inject the aci_override_linked_account_owner_id parameter for the ACI_EXECUTE_FUNCTION tool call
                        # to override the linked_account_owner_id parameter
                        if tool_name == ACIExecuteFunction.get_name():
                            tool_args["aci_override_linked_account_owner_id"] = ACI_OVERRIDE_LINKED_ACCOUNT_OWNER_ID

                        result = await self.session.call_tool(tool_name, tool_args)
                        print(f"[Tool {tool_name} result: {result.content}]")

                        messages.append({
                            "role": "user",
                            "content": [{"type": "tool_result", "tool_use_id": content.id, "content": result.content}]
                        })


            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()    


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()

        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())        