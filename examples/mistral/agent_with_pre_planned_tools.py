import json
import os

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from dotenv import load_dotenv
from mistralai import Mistral
from rich import print as rprint
from rich.panel import Panel

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


# gets MISTRAL_API_KEY from your environment variables
mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
# gets ACI_API_KEY from your environment variables
aci = ACI()


def main() -> None:
    # For a list of all supported apps and functions, please go to the platform.aci.dev
    brave_search_function_definition = aci.functions.get_definition(
        "BRAVE_SEARCH__WEB_SEARCH"
    )

    rprint(Panel("Brave search function definition", style="bold blue"))
    rprint(brave_search_function_definition)

    response = mistral.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant with access to a variety of tools.",
            },
            {
                "role": "user",
                "content": "What is aipolabs ACI?",
            },
        ],
        tools=[brave_search_function_definition],
        tool_choice="required",  # force the model to generate a tool call for demo purposes
    )
    tool_call = (
        response.choices[0].message.tool_calls[0]
        if response.choices[0].message.tool_calls
        else None
    )

    if tool_call:
        rprint(Panel(f"Tool call: {tool_call.function.name}", style="bold green"))
        rprint(f"arguments: {tool_call.function.arguments}")
        # submit the selected function and its arguments to aipolabs ACI backend for execution
        result = aci.handle_function_call(
            tool_call.function.name,
            json.loads(tool_call.function.arguments),
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
        rprint(Panel("Function Call Result", style="bold yellow"))
        rprint(result)


if __name__ == "__main__":
    main()
