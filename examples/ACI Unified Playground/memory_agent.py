import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
import json
import nest_asyncio

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.toolkits.mcp_toolkit import MCPConnectionError
from camel.types import ModelPlatformType
from create_config import create_config

# Apply nest_asyncio to allow running asyncio in a uvicorn environment
nest_asyncio.apply()

load_dotenv()
console = Console()

# Global variables for the agent and toolkit
agent: ChatAgent | None = None
mcp_toolkit: MCPToolkit | None = None
tool_list: list[dict] = []
agent_name = "ACI.dev Unified MCP Agent"

# System message content for the Unified MCP memory management agent
system_message_content = """You are a helpful assistant with access to unlimited number of tools via two meta functions:
- ACI_SEARCH_FUNCTIONS
- ACI_EXECUTE_FUNCTION

Always format your answers in markdown with use of bold italics tables etc wherever needed
You can use ACI_SEARCH_FUNCTIONS to find relevant, executable functions that can help you with your task.
Once you have identified the function you need to use, you can use ACI_EXECUTE_FUNCTION to execute the function provided you have the correct input arguments.

You are specialized in Memory Management using MEM0 tools, web search, and email operations.

**IMPORTANT: Always use user_id "parthshr370" in all MEM0 tool calls.**

**You have access to unlimited tools through dynamic discovery:**

**Your Workflow:**
1. **Analyze User Intent:** Determine what the user wants to accomplish (memory operations, web search, email tasks, etc.)
2. **Search for Tools:** Use ACI_SEARCH_FUNCTIONS with a descriptive intent to find the most relevant functions
3. **Execute Functions:** Use ACI_EXECUTE_FUNCTION to run the discovered functions with proper parameters
4. **Respond Conversationally:** Provide natural, helpful responses about the results

**Key Principles:**
- **For Memory Operations:** Search for "MEM0" functions and always include user_id "parthshr370" in parameters
- Whenever I ask you some personal detail such as that of my daugheter or my medical status just use MEM0 for that and normal generic searches use BRAVE_SEARCH as usual
- **For Web Search:** Search for "BRAVE_SEARCH" or "web search" functions when users need current information
- **For Email Tasks:** Search for "GMAIL" functions for email-related operations. When users ask about "latest email" or "recent emails", automatically get the full message content, not just the ID.
- **Function Discovery:** Be specific in your search intent (e.g., "store user memories in MEM0" rather than just "memory")
- **Complete Execution:** Always complete the full task in one interaction. Don't ask for permission to continue - just do it.

**Example Workflows:**

*Memory Storage Example:*
User: "I went to Paris last week and loved the Eiffel Tower"
1. Use ACI_SEARCH_FUNCTIONS with intent: "store user travel memories and experiences in MEM0"
2. Use ACI_EXECUTE_FUNCTION to execute the found MEM0 storage function with user_id "parthshr370"
3. Respond conversationally about what was stored

*Memory Retrieval Example:*
User: "What do you remember about my travels?"
1. Use ACI_SEARCH_FUNCTIONS with intent: "retrieve and search user travel memories from MEM0"
2. Use ACI_EXECUTE_FUNCTION to search memories with user_id "parthshr370"
3. Present the results in a friendly, organized format

*Web Search Example:*
User: "What's the current weather in Paris?"
1. Use ACI_SEARCH_FUNCTIONS with intent: "search web for current weather information"
2. Use ACI_EXECUTE_FUNCTION to perform the web search
3. Share the current weather information

*Email Example:*
User: "What is my latest Gmail inbox mail?"
1. Use ACI_SEARCH_FUNCTIONS with intent: "get latest Gmail inbox messages"
2. Use ACI_EXECUTE_FUNCTION to list recent messages
3. Automatically get the full content of the latest message
4. Present the complete email details (subject, sender, content)

**Response Format:**
- Start with natural conversation
- **Action Taken:** Brief explanation of what tools were used
- **Results:** Present information clearly and organized
- **Status:** Confirm success and provide context
- End with helpful follow-up suggestions

Always be proactive in using the search and execute functions to find the best tools for each user request. The Unified MCP server gives you access to all available functions dynamically - use this power wisely to provide the best user experience."""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the application, including agent setup and teardown.
    """
    global agent, mcp_toolkit, tool_list
    rprint(Panel("[bold yellow]Initializing Services and Agent...[/bold yellow]"))
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")

    # Connect to MCP server with retries
    max_retries = 3
    retry_delay_seconds = 5
    for attempt in range(max_retries):
        try:
            console.log(
                f"Attempting to connect to MCP server ({attempt + 1}/{max_retries})..."
            )
            await mcp_toolkit.connect()
            console.log("[bold green]✓ Services Connected.[/bold green]")
            break
        except MCPConnectionError as e:
            if attempt < max_retries - 1:
                console.log(
                    f"[yellow]Connection failed. Retrying in {retry_delay_seconds} seconds...[/yellow]"
                )
                await asyncio.sleep(retry_delay_seconds)
            else:
                console.log(
                    "[bold red]FATAL: MCP connection failed after multiple retries.[/bold red]"
                )
                raise e

    # Define the Agent's persona as a Memory Management Agent
    memory_agent_prompt = BaseMessage.make_assistant_message(
        role_name=agent_name,
        content=system_message_content,
    )

    # Create the AI Agent
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.0, "max_tokens": 70000},
    )
    tools = mcp_toolkit.get_tools()

    # Store a serializable list of tool information
    tool_list = [
        {"name": tool.func.__name__, "description": tool.func.__doc__ or ""}
        for tool in tools
    ]

    rprint(
        f"[bold blue]Available tools:[/bold blue] {[tool['name'] for tool in tool_list]}"
    )

    agent = ChatAgent(model=model, system_message=memory_agent_prompt, tools=tools)
    agent.reset()
    console.print(Panel(f"[bold green]{agent_name} is ready![/bold green]"))

    yield  # The application is now running

    # --- Teardown ---
    if mcp_toolkit:
        await mcp_toolkit.disconnect()
        rprint("\n[bold red]Disconnected from services. Program ended.[/bold red]")


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserMessage(BaseModel):
    content: str

class ConfigUpdate(BaseModel):
    linkedAccountOwnerId: str
    aciApiKey: str


@app.get("/tools")
async def get_tools():
    """
    Endpoint to get the list of available tools.
    """
    if not tool_list:
        rprint("[bold red]Tools not available yet.[/bold red]")
        return {"error": "Tools not available yet."}

    rprint(
        f"[bold blue]Returning tools list:[/bold blue] {[tool['name'] for tool in tool_list]}"
    )
    return {"tools": tool_list}

@app.get("/config")
async def get_config():
    """
    Endpoint to get the current configuration.
    """
    try:
        # Read current config from environment and config.json
        linked_account_owner_id = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
        aci_api_key = os.getenv("ACI_API_KEY", "")
        
        return {
            "linkedAccountOwnerId": linked_account_owner_id,
            "aciApiKey": "••••••••" if aci_api_key else ""  # Mask the API key
        }
    except Exception as e:
        rprint(f"[bold red]Error getting config: {e}[/bold red]")
        return {"error": "Could not get configuration"}

@app.post("/config")
async def update_config(config_update: ConfigUpdate):
    """
    Endpoint to update configuration. Updates both .env file and config.json.
    """
    try:
        rprint(f"[bold magenta]Received config update request[/bold magenta]")
        
        # Update .env file
        env_lines = []
        env_file_path = ".env"
        
        # Read existing .env file if it exists
        if os.path.exists(env_file_path):
            with open(env_file_path, "r") as f:
                env_lines = f.readlines()
        
        # Update or add the configuration values
        updated_lines = []
        linked_id_updated = False
        api_key_updated = False
        
        for line in env_lines:
            if line.strip().startswith("LINKED_ACCOUNT_OWNER_ID="):
                updated_lines.append(f"LINKED_ACCOUNT_OWNER_ID={config_update.linkedAccountOwnerId}\n")
                linked_id_updated = True
            elif line.strip().startswith("ACI_API_KEY=") and config_update.aciApiKey != "••••••••":
                updated_lines.append(f"ACI_API_KEY={config_update.aciApiKey}\n")
                api_key_updated = True
            else:
                updated_lines.append(line)
        
        # Add new lines if they weren't found
        if not linked_id_updated:
            updated_lines.append(f"LINKED_ACCOUNT_OWNER_ID={config_update.linkedAccountOwnerId}\n")
        if not api_key_updated and config_update.aciApiKey != "••••••••":
            updated_lines.append(f"ACI_API_KEY={config_update.aciApiKey}\n")
        
        # Write updated .env file
        with open(env_file_path, "w") as f:
            f.writelines(updated_lines)
        
        # Update environment variables for current session
        os.environ["LINKED_ACCOUNT_OWNER_ID"] = config_update.linkedAccountOwnerId
        if config_update.aciApiKey != "••••••••":
            os.environ["ACI_API_KEY"] = config_update.aciApiKey
        
        # Regenerate config.json with new values
        create_config()
        
        rprint("[bold green]✓ Configuration updated successfully[/bold green]")
        return {"success": True, "message": "Configuration updated. Please restart the server for changes to take effect."}
        
    except Exception as e:
        rprint(f"[bold red]Error updating config: {e}[/bold red]")
        return {"error": f"Failed to update configuration: {str(e)}"}


@app.post("/chat")
async def chat_endpoint(user_message: UserMessage):
    """
    Endpoint to receive user messages and return the agent's response.
    """
    rprint(f"[bold magenta]Received request for /chat[/bold magenta]")
    rprint(f"[cyan]User content:[/cyan] {user_message.content}")

    if not agent:
        rprint("[bold red]Agent not initialized[/bold red]")
        return {"error": "Agent not initialized"}

    message = BaseMessage.make_user_message(
        role_name="User", content=user_message.content
    )

    with console.status("[bold green]Agent is working...[/bold green]"):
        rprint("[yellow]Invoking agent...[/yellow]")
        response = await agent.astep(message)
        rprint("[green]Agent invocation complete.[/green]")

    executed_tools = []
    tool_calls_details = []

    if response.info and response.info.get("tool_calls"):
        executed_tools = [
            tool_call.tool_name for tool_call in response.info["tool_calls"]
        ]

        # Create detailed tool calls information for frontend
        tool_calls_details = []
        for tool_call in response.info["tool_calls"]:
            detail = {
                "tool_name": tool_call.tool_name,
                "args": tool_call.args,
                "result": str(tool_call.result),
                "result_preview": str(tool_call.result)[:200] + "..."
                if len(str(tool_call.result)) > 200
                else str(tool_call.result),
            }

            # For Unified MCP, extract the actual function name from args if it's ACI_EXECUTE_FUNCTION
            if tool_call.tool_name == "ACI_EXECUTE_FUNCTION" and tool_call.args.get(
                "function_name"
            ):
                detail["actual_function"] = tool_call.args["function_name"]
                detail["function_arguments"] = tool_call.args.get(
                    "function_arguments", {}
                )

            tool_calls_details.append(detail)

        rprint(
            f"[blue]Tools called:[/blue]\n{json.dumps([{k: v for k, v in detail.items() if k != 'result'} for detail in tool_calls_details], indent=2)}"
        )

    if response and hasattr(response, "msgs") and response.msgs:
        response_content = response.msgs[0].content
        rprint(
            f"[cyan]Agent response content (preview):[/cyan]\n{response_content[:200]}..."
        )
        return {
            "response": response_content,
            "executed_tools": executed_tools,
            "tool_details": tool_calls_details,
            "raw_output": str(response),
        }

    rprint("[bold red]No response generated.[/bold red]")
    return {"error": "Sorry, I couldn't respond."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for chat.
    """
    await websocket.accept()
    rprint("[bold green]WebSocket connection established.[/bold green]")

    if not mcp_toolkit or not agent:
        rprint("[bold red]Agent or toolkit not initialized.[/bold red]")
        await websocket.send_json({"type": "error", "content": "Agent not initialized"})
        return

    try:
        while True:
            data = await websocket.receive_text()
            rprint(f"[cyan]WebSocket received:[/cyan] {data}")

            user_message = BaseMessage.make_user_message(role_name="User", content=data)
            response = await agent.astep(user_message)

            if response and hasattr(response, "msgs") and response.msgs:
                for msg in response.msgs:
                    # Send formatted message
                    await websocket.send_json(
                        {
                            "type": "agent_response",
                            "sender": agent_name,
                            "content": msg.content,
                        }
                    )
                # Send raw output
                await websocket.send_json(
                    {
                        "type": "raw_output",
                        "sender": "System",
                        "content": str(response),
                    }
                )
                rprint("[green]WebSocket response sent.[/green]")

    except WebSocketDisconnect:
        rprint("[bold yellow]WebSocket connection closed.[/bold yellow]")
    except Exception as e:
        rprint(f"[bold red]An error occurred in WebSocket: {e}[/bold red]")
        try:
            await websocket.send_json(
                {"type": "error", "sender": "System", "content": str(e)}
            )
        except:
            pass
    finally:
        rprint("[bold yellow]WebSocket connection terminated.[/bold yellow]")


if __name__ == "__main__":
    import uvicorn

    rprint(Panel("[bold green]Starting ACI.dev MEM0 Demo Server...[/bold green]"))
    uvicorn.run(app, host="0.0.0.0", port=8000)
