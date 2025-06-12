#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rich import print as rprint
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.toolkits import ACIToolkit
from pprint import pprint
import json

load_dotenv()

def summarize_tool_outputs(agent, response, query):
    """
    Summarize the results of tool calls and generate a natural language response.
    
    Args:
        agent: The chat agent instance
        response: The response containing tool call results
        query: The original user query
        
    Returns:
        str: A natural language summary of the tool call results
    """
    tool_calls = response.info.get("tool_calls", [])
    if not tool_calls:
        # Return original response if no tools were called
        rprint("\n[dim]No tools were called[/dim]")
        return response.msg.content
    else:
        # Process tool call results and generate summary
        structured_results = {record.tool_name: record.result for record in tool_calls}
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
        # model_type="gemini-2.5-pro-preview-05-06",
        model_type="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.5, "max_tokens": 4000},
    )

    # Create and initialize chat agent with tools
    agent = ChatAgent(model=model, tools=tools)
    rprint("[green]Agent ready[/green]")

    # Get user input
    query = input("\nEnter your query: ")

    rprint("\n[yellow]Processing...[/yellow]")
    # Execute agent step with user query - may trigger multiple tool calls
    response = agent.step(query)
    
    # Display response and tool call information
    rprint(f"[dim]Response: {response}[/dim]")
    rprint(f"\nFound [cyan]{len(response.info['tool_calls'])}[/cyan] tool calls:")
    for count,tool_call in enumerate(response.info['tool_calls']):
        rprint(f"[dim]Tool call {count+1}: {tool_call}[/dim]")
        rprint(f"[dim]Tool call {count+1} result: {tool_call.result}[/dim]")

    # Generate and display summary of tool call results
    summary = summarize_tool_outputs(agent, response, query)
    rprint(f"\n[dim]Final output: {summary}[/dim]")

    rprint("\n[green]Done[/green]")


if __name__ == "__main__":
    main()
