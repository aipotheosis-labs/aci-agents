import json
import os

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from dotenv import load_dotenv
from openai import OpenAI
from rich import print as rprint
from rich.panel import Panel

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()
# gets ACI_API_KEY from your environment variables
aci = ACI()


def main() -> None:
    # For a list of all supported apps and functions, please go to the platform.aci.dev
    brave_search_function_definition = aci.functions.get_definition(
        "BRAVE_SEARCH__WEB_SEARCH"
    )
    rprint(Panel("Brave search function definition", style="bold blue"))
    rprint(brave_search_function_definition)

    github_star_repository_function_definition = aci.functions.get_definition(
        "GITHUB__STAR_REPOSITORY"
    )
    rprint(Panel("Github star repository function definition", style="bold blue"))
    rprint(github_star_repository_function_definition)

    messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with access to a variety of tools.",
            },
            {
                "role": "user",
                # "content": "What is aipolabs ACI?",
                "content": "Star the repo https://github.com/aipotheosis-labs/aci, then search information about ACI.dev.",
            },
    ]
    # Loop until no tool_call (with max iterations for safety)
    max_iterations = 10
    iteration_count = 0
    while iteration_count < max_iterations:
        iteration_count += 1
        # Call model
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=[brave_search_function_definition, github_star_repository_function_definition],
                tool_choice="auto",  # let the model decide when to use tools
            )
            # Convert ChatCompletionMessage to dictionary format
            assistant_message = {
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls
            }
            messages.append(assistant_message)
        except Exception as e:
            rprint(Panel(f"Error calling LLM: {e}", style="bold red"))
            break
        
        # Get tool calls
        tool_calls = response.choices[0].message.tool_calls if response.choices[0].message.tool_calls else []
        if tool_calls:
            # Execute tool calls one by one
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                
                rprint(Panel(f"Tool call: {tool_name}", style="bold yellow"))
                rprint(f"arguments: {tool_args}")

                # submit the selected function and its arguments to aipolabs ACI backend for execution
                try:
                    result = aci.handle_function_call(
                        tool_name,
                        json.loads(tool_args),
                        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                        allowed_apps_only=True,
                        format=FunctionDefinitionFormat.OPENAI,
                    )
                    """
                    alternatively, because this is a direct function execution you can use the following:
                    result = aci.functions.execute(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments),
                        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                    )
                    """
                except Exception as e:
                    result = f"Error executing tool {tool_name}: {e}"
                    rprint(Panel(f"Tool execution error: {e}", style="bold red"))
                
                rprint(Panel("Function Call Result", style="bold yellow"))
                rprint(result)

                # Add tool execution result back to message list
                tool_message = {
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call.id
                }
                messages.append(tool_message)
        else:
            rprint(Panel("Final AI Response", style="bold green"))
            rprint(messages[-1]["content"])
            break

if __name__ == "__main__":
    main()
