import json
import os

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from crewai import Agent, Task
from crewai.tools import tool
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


@tool
def github_star_repository(owner: str, repo: str) -> str:
    """Star a GitHub repository by providing the owner and repo name"""
    aci = ACI()

    result = aci.handle_function_call(
        "GITHUB__STAR_REPOSITORY",
        {"path": {"owner": owner, "repo": repo}},
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        format=FunctionDefinitionFormat.ANTHROPIC,
    )
    return json.dumps(result)

@tool
def github_get_user(username: str) -> str:
    """Get a GitHub user by providing the username"""
    aci = ACI()

    result = aci.handle_function_call(
        "GITHUB__GET_USER",
        {"path": {"username": username}},
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        format=FunctionDefinitionFormat.ANTHROPIC,
    )
    return json.dumps(result)


def main() -> None:
    agent = Agent(
        role="Assistant",
        backstory="You are a helpful assistant that can use available tools to help the user.",
        goal="Help with user requests",
        tools=[github_star_repository, github_get_user],
        function_calling_llm="gpt-4o-mini",
        verbose=True,
    )

    task = Task(
        description="Star the repo https://github.com/aipotheosis-labs/aci, and get the user information for the user aipotheosis-labs",
        expected_output="A natural language summary of both operations: whether the repository was successfully starred and key information about the GitHub user.",
    )

    response = agent.execute_task(task)
    rprint(response)


if __name__ == "__main__":
    main()
