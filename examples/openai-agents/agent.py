import asyncio
import json
import os
from typing import Any

from aci import ACI
from agents import Agent, FunctionTool, RunContextWrapper, Runner
from dotenv import load_dotenv

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

aci = ACI()


github_star_repository_function_definition = aci.functions.get_definition(
    "GITHUB__STAR_REPOSITORY"
)
print(github_star_repository_function_definition)


async def run_function(ctx: RunContextWrapper[Any], args: str) -> str:
    result = aci.handle_function_call(
        github_star_repository_function_definition["function"]["name"],
        json.loads(args),
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
    )
    return result


tool = FunctionTool(
    name=github_star_repository_function_definition["function"]["name"],
    description=github_star_repository_function_definition["function"]["description"],
    params_json_schema=github_star_repository_function_definition["function"]["parameters"],
    on_invoke_tool=run_function,
)


github_agent = Agent(
    name="github_agent",
    instructions="You are a helpful assistant that can use available tools to help the user.",
    tools=[tool],
)


async def main() -> None:
    result = await Runner.run(
        starting_agent=github_agent,
        input="Star the repo https://github.com/aipotheosis-labs/aci",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
