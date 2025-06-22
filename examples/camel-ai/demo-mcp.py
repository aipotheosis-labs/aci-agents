#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
from rich import print as rprint
from collections import defaultdict
import json

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType

load_dotenv()

def summarize_tool_outputs(model, response, query):
    """
    Summarize the results of tool calls and generate a natural language response.
    
    Args:
        model: The model instance
        response: The response containing tool call results
        query: The original user query
        
    Returns:
        str: A natural language summary of the tool call results
    """
    summariser_system_msg = BaseMessage.make_assistant_message(
        role_name="Summariser",
        content="You summarise tool outputs without calling any tools."
    )
    agent = ChatAgent(
        system_message=summariser_system_msg,
        model=model,
        tools=[]  # ensure no tool recursion
    )        
    info = getattr(response, "info", {})
    tool_calls = info.get("tool_calls", [])
    # Return original response if no tools were called
    if not tool_calls:
        rprint("\n[dim]No tools were called[/dim]")
        if hasattr(response, "msg") and response.msg:
            return response.msg.content
        if hasattr(response, "msgs") and response.msgs:
            return response.msgs[-1].content
        return str(response)

    # Process tool call results and generate summary
    structured_results: dict[str, list] = defaultdict(list)
    for record in tool_calls:
        # Ensure every value is JSON-serialisable
        value = record.result
        if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
            value = str(value)
        structured_results[record.tool_name].append(value)

    tool_outputs_json = json.dumps(structured_results, ensure_ascii=False, indent=2)
    rprint(f"\n[dim]Tool outputs: {tool_outputs_json}[/dim]")
    summary_prompt = f"""Please summarize the following tool call results:{tool_outputs_json} and answer the user's question:{query} in natural language."""
    summary_response = agent.step(summary_prompt)
    rprint(f"\n[dim]Summary response: {summary_response}[/dim]")
    return summary_response.msg.content

async def main():
    from create_config import create_config
    
    rprint("[green]CAMEL AI Agent with MCP Toolkit[/green]")
    
    # create config for mcp server
    create_config()

    # connect to mcp server
    rprint("Connecting to MCP server...")
    try:
        mcp_toolkit = MCPToolkit(config_path="config.json")
        await mcp_toolkit.connect()
        tools = mcp_toolkit.get_tools()
        rprint(f"Connected successfully. Found [cyan]{len(tools)}[/cyan] tools available")
    except Exception as e:
        rprint(f"[red]Failed to connect to MCP server: {e}[/red]")
        rprint("[yellow]Please check if MCP server is running and config.json is correct[/yellow]")
        return

    # setup gemini model
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.0-flash-001", # gemini-2.5-pro-preview-05-06
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.7, "max_tokens": 4000},
    )

    system_message = BaseMessage.make_assistant_message(
        role_name="Assistant",
        content="You are a helpful assistant with access to search, GitHub, and arXiv tools.",
    )

    # create camel agent
    agent = ChatAgent(
        system_message=system_message, 
        model=model, 
        tools=tools, 
        memory=None
    )

    rprint("[green]Agent ready[/green]")
    
    # get user query
    query = input("\nEnter your query: ")

    rprint("\n[yellow]Processing...[/yellow]")
    
    try:
        # Execute agent step with user query - may trigger multiple tool calls
        response = agent.step(query)
        
        # Display response and tool call information - 参考demo.py的逻辑
        rprint(f"[dim]Response: {response}[/dim]")
        tool_calls = response.info.get("tool_calls", [])
        rprint(f"\nFound [cyan]{len(tool_calls)}[/cyan] tool calls:")
        for idx, tc in enumerate(tool_calls, start=1):
            rprint(f"[dim]Tool call {idx}: {tc}[/dim]")
            rprint(f"[dim]Tool call {idx} result: {getattr(tc, 'result', 'N/A')}[/dim]")

        # Generate and display summary of tool call results
        summary = summarize_tool_outputs(model, response, query)
        rprint(f"\n[bold]Final Answer:[/bold] {summary}")
        
    except Exception as e:
        rprint(f"[red]Error during processing: {e}[/red]")
        rprint("[yellow]This might be due to MCP server timeout or tool execution issues[/yellow]")
    
    finally:
        # disconnect from mcp
        try:
            await mcp_toolkit.disconnect()
            rprint("[green]MCP connection closed[/green]")
        except Exception as e:
            rprint(f"[yellow]Warning: Error disconnecting MCP: {e}[/yellow]")
    
    rprint("\n[green]Done[/green]")

def run_main():
    """Wrapper function to handle asyncio properly on Windows"""
    try:
        # 在Windows上强制使用SelectorEventLoopPolicy来解决子进程问题
        if os.name == 'nt':  # Windows
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(main())
    except KeyboardInterrupt:
        rprint("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        rprint(f"[red]Fatal error: {e}[/red]")
        import traceback
        rprint(f"[dim]{traceback.format_exc()}[/dim]")

if __name__ == "__main__":
    run_main()