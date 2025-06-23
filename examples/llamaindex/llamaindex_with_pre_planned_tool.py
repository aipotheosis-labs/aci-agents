import asyncio
import json
import os

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from dotenv import load_dotenv
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from rich import print as rprint
from rich.panel import Panel

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


def github_star_repository(owner: str, repo: str) -> str:
    """Star a GitHub repository by providing the owner and repo name"""
    rprint(Panel("Function Call: github_star_repo", style="bold yellow"))
    rprint(f"Parameters(github_star_repo): owner = {owner}, repo = {repo}")
    aci = ACI()

    result = aci.handle_function_call(
        "GITHUB__STAR_REPOSITORY",
        {"path": {"owner": owner, "repo": repo}},
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        format=FunctionDefinitionFormat.OPENAI,
    )
    rprint(Panel("Function(GITHUB__STAR_REPOSITORY) Call Result", style="bold magenta"))
    rprint(result)
    return json.dumps(result)

def github_get_user(username: str) -> str:
    """Get a GitHub user by providing the username"""
    rprint(Panel("Function Call: github_get_user", style="bold yellow"))
    rprint(f"Parameters(github_get_user): username = {username}")
    aci = ACI()

    result = aci.handle_function_call(
        "GITHUB__GET_USER",
        {"path": {"username": username}},
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        format=FunctionDefinitionFormat.OPENAI,
    )
    rprint(Panel("Function(GITHUB__GET_USER) Call Result", style="bold magenta"))
    rprint(result)
    return json.dumps(result)


# GITHUB__GET_REPOSITORY_LANGUAGES
def github_get_repository_languages(owner: str, repo: str) -> str:
    """Get the languages used in a GitHub repository by providing the owner and repo name"""
    rprint(Panel("Function Call: github_get_repository_languages", style="bold yellow"))
    rprint(f"Parameters(github_get_repository_languages): owner = {owner}, repo = {repo}")
    aci = ACI()
    
    result = aci.handle_function_call(
        "GITHUB__GET_REPOSITORY_LANGUAGES",
        {"path": {"owner": owner, "repo": repo}},
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        format=FunctionDefinitionFormat.OPENAI,
    )
    rprint(Panel("Function(GITHUB__GET_REPOSITORY_LANGUAGES) Call Result", style="bold magenta"))
    rprint(result)
    return json.dumps(result)



async def main() -> None:
    agent = FunctionAgent(
        tools=[github_star_repository, github_get_user, github_get_repository_languages],
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt="You are a helpful assistant that can use available tools to help the user.",
    )

    response = await agent.run("Star the repo https://github.com/aipotheosis-labs/aci and get the languages used in the repo, then get the user info for aipotheosis-labs.")
    
    # Format the output
    rprint(Panel("🤖 Raw Output", style="bold blue"))
    rprint(response)
    rprint(Panel("🤖 Text Output", style="bold blue"))
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
