import os

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich import print as rprint
from rich.panel import Panel
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage, HumanMessage
from typing import List

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

def main() -> None:
    aci = ACI()
    github_star_repository_function_definition = aci.functions.get_definition(
        "GITHUB__STAR_REPOSITORY"
    )
    rprint(Panel("Github star repository function definition", style="bold blue"))
    rprint(github_star_repository_function_definition)

    brave_search_web_search_function_definition = aci.functions.get_definition(
        "BRAVE_SEARCH__WEB_SEARCH"
    )
    rprint(Panel("Brave search web search function definition", style="bold blue"))
    rprint(brave_search_web_search_function_definition)

    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools([github_star_repository_function_definition, brave_search_web_search_function_definition])
    
    # initial messages
    messages: List[BaseMessage] = [HumanMessage(content="Star the repo https://github.com/aipotheosis-labs/aci, then search information about ACI.dev.")]
    
    # Loop until no tool_call (with max iterations for safety)
    max_iterations = 10
    iteration_count = 0
    while iteration_count < max_iterations:
        iteration_count += 1
        # Call model
        try:
            ai_message: AIMessage = llm_with_tools.invoke(messages)
            messages.append(ai_message)
        except Exception as e:
            rprint(Panel(f"Error calling LLM: {e}", style="bold red"))
            break
        
        # Check if contains tool calls
        if not hasattr(ai_message, "tool_calls") or not ai_message.tool_calls:
            # No tool calls, this is the final response
            break
            
        # Has tool calls, execute them one by one
        for tool_call in ai_message.tool_calls:
            # Validate tool call structure
            if not all(key in tool_call for key in ["name", "args", "id"]):
                rprint(Panel(f"Invalid tool call structure: {tool_call}", style="bold red"))
                continue
                
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            rprint(Panel(f"Tool call: {tool_name}", style="bold yellow"))
            rprint(f"arguments: {tool_args}")
            
            # Execute tool call
            try:
                result = aci.handle_function_call(
                    tool_name,
                    tool_args,
                    linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                    format=FunctionDefinitionFormat.OPENAI,
                    )
            except Exception as e:
                result = f"Error executing tool {tool_name}: {e}"
                rprint(Panel(f"Tool execution error: {e}", style="bold red"))
            
            
            rprint(Panel("Function Call Result", style="bold magenta"))
            rprint(result)
            
            # Add tool execution result back to message list
            tool_message = ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
            messages.append(tool_message)
    
    # Print final AI response
    rprint(Panel("Final AI Response", style="bold green"))
    # Find the last AIMessage in the conversation
    last_ai_message = None
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            last_ai_message = message
            break
    
    if last_ai_message:
        rprint(last_ai_message.content)
    else:
        rprint("No AI response found")


if __name__ == "__main__":
    main()