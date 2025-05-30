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
    
    # Loop until no tool_call
    while True:
        # Call model
        ai_message: AIMessage = llm_with_tools.invoke(messages)
        messages.append(ai_message)
        
        # Check if contains tool calls
        if not hasattr(ai_message, "tool_calls") or not ai_message.tool_calls:
            # No tool calls, this is the final response
            break
            
        # Has tool calls, execute them one by one
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            rprint(Panel(f"Tool call: {tool_name}", style="bold yellow"))
            rprint(f"arguments: {tool_args}")
            
            # Execute tool call
            result = aci.handle_function_call(
                tool_name,
                tool_args,
                linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                format=FunctionDefinitionFormat.OPENAI,
            )
            
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
    rprint(messages[-1].content)


if __name__ == "__main__":
    main()