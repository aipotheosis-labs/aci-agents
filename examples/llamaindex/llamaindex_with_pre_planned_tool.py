import asyncio
import json
import os
from typing import Callable

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from dotenv import load_dotenv
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from rich import print as rprint


def github_star_repository(owner: str, repo: str) -> str:
    """Star a GitHub repository by providing the owner and repo name"""
    rprint(Panel("Function Call: github_star_repo", style="bold yellow"))
    rprint(f"Parameters(github_star_repo): owner = {owner}, repo = {repo}")

    aci = ACI()

    # 1. get the function definition from ACI
    function_definition = aci.functions.get_definition(function_name, format=format)

    # 2. extract information from the schema
    if format == FunctionDefinitionFormat.OPENAI:
        name = function_definition["function"]["name"]
        description = function_definition["function"]["description"]
        inputs = function_definition["function"]["parameters"]
    elif format == FunctionDefinitionFormat.OPENAI_RESPONSES:
        name = function_definition["name"]
        description = function_definition["description"]
        inputs = function_definition["parameters"]
    elif format == FunctionDefinitionFormat.ANTHROPIC:
        name = function_definition["name"]
        description = function_definition["description"]
        inputs = function_definition["input_schema"]
    else:
        raise ValueError(f"Unsupported function format: {format}")

    # 3. create a function implementation
    def implementation(function_parameters: str) -> str:
        return aci.handle_function_call(
            name,
            json.loads(function_parameters),
            linked_account_owner_id=linked_account_owner_id,
            allowed_apps_only=True,
            format=FunctionDefinitionFormat.ANTHROPIC,
        )

    # 4. update implementation funcion name and docstring
    implementation.__name__ = name

    doc_lines = [description, ""]
    doc_lines.append("Args:")
    doc_lines.append(
        f"    function_parameters (str): JSON string of the function's parameters. The schema for this JSON string is defined in the following JSON schema: {json.dumps(inputs)}"
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
