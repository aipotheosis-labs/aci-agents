import json
import os

from aci import ACI
from aci.meta_functions import ACISearchFunctions, ACIExecuteFunction
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

prompt = (
    "You are a helpful assistant with access to a unlimited number of tools via some meta functions: "
    "ACI_SEARCH_FUNCTIONS, and ACI_EXECUTE_FUNCTION."
    "You can use ACI_SEARCH_FUNCTIONS to find relevant functions across all apps. Try to limit the number of results per request to 1."
    "Once you have identified the function you need to use, you can use ACI_EXECUTE_FUNCTION to execute the function provided you have the correct input arguments."
    "IMPORTANT: When calling any function, carefully read the function definition and ensure you provide ALL required parameters with correct names and types. "
    "Always check the function schema before making function calls to avoid validation errors."
)

# aipolabs meta functions for the LLM to discover the available executale functions dynamically
tools_meta = [
    ACISearchFunctions.to_json_schema(FunctionDefinitionFormat.OPENAI),
    ACIExecuteFunction.to_json_schema(FunctionDefinitionFormat.OPENAI),
]


def main() -> None:
    # Start the LLM processing loop
    chat_history: list[dict] = []

    while True:
        rprint(Panel("Waiting for LLM Output", style="bold blue"))
        response = openai.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": "Can you use brave search to find top 5 results about aipolabs ACI? Then star the repo https://github.com/aipotheosis-labs/aci",
                },
            ]
            + chat_history,
            tools=tools_meta,
            # tool_choice="required",  # force the model to generate a tool call
            parallel_tool_calls=False,
        )

        # Process LLM response and potential function call (there can only be at most one function call)
        content = response.choices[0].message.content
        tool_call = (
            response.choices[0].message.tool_calls[0]
            if response.choices[0].message.tool_calls
            else None
        )
        if content:
            rprint(Panel("LLM Message", style="bold green"))
            rprint(content)
            chat_history.append({"role": "assistant", "content": content})

        # Handle function call if any
        if tool_call:
            rprint(
                Panel(f"Function Call: {tool_call.function.name}", style="bold yellow")
            )
            rprint(f"arguments: {tool_call.function.arguments}")

            chat_history.append({"role": "assistant", "tool_calls": [tool_call]})
            result = aci.handle_function_call(
                tool_call.function.name,
                json.loads(tool_call.function.arguments),
                linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                allowed_apps_only=True,
                format=FunctionDefinitionFormat.OPENAI,
            )

            rprint(Panel("Function Call Result", style="bold magenta"))
            rprint(result)
            # Continue loop, feeding the result back to the LLM for further instructions
            chat_history.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )
        else:
            # If there's no further function call, exit the loop
            rprint(Panel("Task Completed", style="bold green"))
            break


if __name__ == "__main__":
    main()
