import json
import os
from typing import Callable

from aci import ACI
from aci.types.functions import FunctionDefinitionFormat
from crewai import Agent, Task
from crewai.tools import tool
from dotenv import load_dotenv
from rich import print as rprint

def build_aci_function(
    function_name: str,
    linked_account_owner_id: str,
    format: FunctionDefinitionFormat = FunctionDefinitionFormat.OPENAI,
) -> Callable[[str], str]:
    """
    Create a Python function from an ACI function schema.
    """
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

    implementation.__doc__ = "\n".join(doc_lines)

    return implementation


load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


def main() -> None:
    agent = Agent(
        role="Assistant",
        backstory="You are a helpful assistant that can use available tools to help the user.",
        goal="Help with user requests",
        tools=[
            tool(
                build_aci_function(
                    "GITHUB__STAR_REPOSITORY",
                    LINKED_ACCOUNT_OWNER_ID,
                    FunctionDefinitionFormat.OPENAI,
                )
            ),
            tool(
                build_aci_function(
                    "GITHUB__GET_USER",
                    LINKED_ACCOUNT_OWNER_ID,
                    FunctionDefinitionFormat.OPENAI,
                )
            ),
        ],
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
