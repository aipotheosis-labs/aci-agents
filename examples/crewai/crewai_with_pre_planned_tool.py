import json
import os

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from crewai import Agent, Task
from crewai.tools import tool
from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


@tool
def github_star_repository(owner: str, repo: str) -> str:
    """Star a GitHub repository by providing the owner and repo name"""
    rprint(Panel("Function Call: github_star_repo", style="bold yellow"))
    rprint(f"Parameters: owner = {owner}, repo = {repo}")
    aci = ACI()

    result = aci.handle_function_call(
        "GITHUB__STAR_REPOSITORY",
        {"path": {"owner": owner, "repo": repo}},
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        format=FunctionDefinitionFormat.ANTHROPIC,
    )
    rprint(Panel("Function Call Result", style="bold magenta"))
    rprint(result)
    return json.dumps(result)


def main() -> None:
    agent = Agent(
        role="Assistant",
        backstory="You are a helpful assistant that can use available tools to help the user.",
        goal="Help with user requests",
        tools=[github_star_repository],
        function_calling_llm="gpt-4o-mini",
        verbose=True,
    )

    task = Task(
        description="Star the repo https://github.com/aipotheosis-labs/aci",
        expected_output="The result of the star operation from the GitHub API",
    )

    response = agent.execute_task(task)
    rprint(response)


if __name__ == "__main__":
    main()
