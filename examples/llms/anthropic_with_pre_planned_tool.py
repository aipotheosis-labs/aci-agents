import os

import anthropic
from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from anthropic.types.content_block import TextBlock, ToolUseBlock
from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


def main() -> None:
    aci = ACI()
    github_get_user_function_definition = aci.functions.get_definition(
        "GITHUB__GET_USER", format=FunctionDefinitionFormat.ANTHROPIC
    )
    rprint(Panel("Github get user function definition", style="bold blue"))
    rprint(github_get_user_function_definition)

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=1,
        system="You are a helpful assistant with access to a variety of tools.",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Tell me about the github user karpathy"}
                ],
            }
        ],
        tools=[github_get_user_function_definition],
    )

    for content_block in response.content:
        if isinstance(content_block, TextBlock):
            rprint(Panel("LLM Response", style="bold green"))
            rprint(content_block.text)
        elif isinstance(content_block, ToolUseBlock):
            rprint(Panel(f"Tool call: {content_block.name}", style="bold yellow"))
            rprint(f"arguments: {content_block.input}")

            result = aci.handle_function_call(
                content_block.name,
                content_block.input,
                linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                format=FunctionDefinitionFormat.ANTHROPIC,
            )

            rprint(Panel("Function Call Result", style="bold magenta"))
            rprint(result)


if __name__ == "__main__":
    main()
