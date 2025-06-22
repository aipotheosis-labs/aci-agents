#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rich import print as rprint
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.toolkits import ACIToolkit
from collections import defaultdict
from camel.messages import BaseMessage
import json

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
        tools=[]# ensure no tool recursion
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


def main():
    """Main function to run the CAMEL AI agent with ACI toolkit."""
    rprint("[green]CAMEL AI with ACI Toolkit[/green]")

    # Initialize with linked account from environment or use default
    linked_account_owner_id = os.getenv("LINKED_ACCOUNT_OWNER_ID", "parthshr370")
    rprint(f"Using account: [cyan]{linked_account_owner_id}[/cyan]")

    # Initialize ACI toolkit and get available tools
    aci_toolkit = ACIToolkit(linked_account_owner_id=linked_account_owner_id)
    tools = aci_toolkit.get_tools()
    
    
    rprint(f"\nTotal tools loaded: [cyan]{len(tools)}[/cyan]")

    # Initialize Gemini model with configuration
    model = ModelFactory.create(
        model_platform="gemini",
        model_type="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.5, "max_tokens": 4000},
    )

    # Create and initialize chat agent with tools
    system_message = BaseMessage.make_assistant_message(
        role_name="Assistant",
        content="You are a helpful assistant with access to the ACI toolkit."
    )
    agent = ChatAgent(
        system_message=system_message,
        model=model,
        tools=tools
    )
    rprint("[green]Agent ready[/green]")

    # Get user input
    query = input("\nEnter your query: ")

    rprint("\n[yellow]Processing...[/yellow]")
    # Execute agent step with user query - may trigger multiple tool calls
    response = agent.step(query)
    
    # Display response and tool call information
    rprint(f"[dim]Response: {response}[/dim]")
    tool_calls = response.info.get("tool_calls", [])
    rprint(f"\nFound [cyan]{len(tool_calls)}[/cyan] tool calls:")
    for idx, tc in enumerate(tool_calls, start=1):
        rprint(f"[dim]Tool call {idx}: {tc}[/dim]")
        rprint(f"[dim]Tool call {idx} result: {getattr(tc, 'result', 'N/A')}[/dim]")

    # Generate and display summary of tool call results
    summary = summarize_tool_outputs(model, response, query)
    rprint(f"\n[dim]Final output: {summary}[/dim]")

    rprint("\n[green]Done[/green]")


if __name__ == "__main__":
    main()
