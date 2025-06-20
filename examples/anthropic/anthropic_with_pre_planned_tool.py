import os

import anthropic
import json
from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
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
    github_star_repository_function_definition = aci.functions.get_definition(
        "GITHUB__STAR_REPOSITORY", format=FunctionDefinitionFormat.ANTHROPIC
    )
    rprint(Panel("Github star repository function definition", style="bold blue"))
    rprint(github_star_repository_function_definition)

    github_get_user_function_definition = aci.functions.get_definition(
        "GITHUB__GET_USER", format=FunctionDefinitionFormat.ANTHROPIC
    )
    rprint(Panel("Github get user function definition", style="bold blue"))
    rprint(github_get_user_function_definition)

    client = anthropic.Anthropic()

    # Initialize message list
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Star the repo https://github.com/aipotheosis-labs/aci, and tell me about the github owner of the repo."}
            ],
        }
    ]

    # Set maximum iterations to prevent infinite loops
    max_iterations = 10
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1
        rprint(Panel(f"Iteration {iteration_count}", style="bold blue"))

        # Call the model
        try:
            response = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
                temperature=1,
                system="You are a helpful assistant with access to a variety of tools.",
                messages=messages,
                tools=[github_star_repository_function_definition,github_get_user_function_definition],
            )
        except Exception as e:
            rprint(Panel(f"Error calling LLM: {e}", style="bold red"))
            break

        # Process response content
        has_tool_call = False
        for content_block in response.content:
            if isinstance(content_block, TextBlock):
                rprint(Panel("LLM Response", style="bold green"))
                rprint(content_block.text)
                # Add AI response to message list
                messages.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": content_block.text}]
                })
            elif isinstance(content_block, ToolUseBlock):
                has_tool_call = True
                rprint(Panel(f"Tool call: {content_block.name}", style="bold yellow"))
                rprint(f"arguments: {content_block.input}")
                # Add tool call to message list
                messages.append({
                    "role": "assistant",
                    "content": [{
                        "type": "tool_use",
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input,
                    }]
                })

                # Execute tool call
                try:
                    result = aci.handle_function_call(
                        content_block.name,
                        content_block.input,
                        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                        format=FunctionDefinitionFormat.ANTHROPIC,
                    )
                except Exception as e:
                    result = f"Error executing tool {content_block.name}: {e}"
                    rprint(Panel(f"Tool execution error: {e}", style="bold red"))

                rprint(Panel("Function Call Result", style="bold magenta"))
                rprint(result)

                # Add tool call result to message list
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }]
                })

        # If no tool call, this is the final response, exit loop
        if not has_tool_call:
            break

    # Print final response
    rprint(Panel("Final Response", style="bold green"))
    for message in messages:
        if message["role"] == "assistant":
            for content in message["content"]:
                if content["type"] == "text":
                    rprint(content["text"])


if __name__ == "__main__":
    main()
