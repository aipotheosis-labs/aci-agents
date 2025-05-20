import asyncio
import json
import os
from typing import Any

from aci import ACI
from aci.types.enums import FunctionDefinitionFormat
from agents import Agent, FunctionTool, RunContextWrapper, Runner
from dotenv import load_dotenv

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

aci = ACI()


def get_tool(function_name: str, linked_account_owner_id: str) -> FunctionTool:
    function_definition = aci.functions.get_definition(function_name)
    name = function_definition["function"]["name"]
    description = function_definition["function"]["description"]
    parameters = function_definition["function"]["parameters"]

    async def tool_impl(
        ctx: RunContextWrapper[Any], args: str
    ) -> str:
        return aci.handle_function_call(
            function_name,
            json.loads(args),
            linked_account_owner_id=linked_account_owner_id,
            allowed_apps_only=True,
            format=FunctionDefinitionFormat.OPENAI,
        )

    return FunctionTool(
        name=name,
        description=description,
        params_json_schema=parameters,
        on_invoke_tool=tool_impl,
        strict_json_schema=True,
    )


github_agent = Agent(
    name="github_agent",
    instructions="You are a helpful assistant that can use available tools to help the user.",
    tools=[get_tool("GITHUB__STAR_REPOSITORY", LINKED_ACCOUNT_OWNER_ID)],
)


async def main() -> None:
    result = await Runner.run(
        starting_agent=github_agent,
        input="Star the repo https://github.com/aipotheosis-labs/aci",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
