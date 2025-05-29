from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext, ToolHardError

from aci import ACI
import os


class GithubGetRepositorySchema(BaseModel):
    """Schema defining the inputs for the GithubGetRepositoryTool."""

    repo: str = Field(..., 
        description="The name of the repository without the .git extension. The name is not case sensitive."
    )
    owner: str = Field(..., 
        description="The account owner of the repository. The name is not case sensitive."
    )


class GithubGetRepositoryTool(Tool):
    """Gets information about a repository from GitHub."""

    id: str = "GITHUB__GET_REPOSITORY"
    name: str = "GITHUB__GET_REPOSITORY"
    description: str = "Gets information about a repository from GitHub"
    args_schema: type[BaseModel] = GithubGetRepositorySchema
    output_schema: tuple[str, str] = ("str", "A string indicating the message sending result")

    def run(self, _: ToolRunContext, owner: str, repo: str) -> str:
        """Run the GithubGetRepositoryTool."""
        aci = ACI()
        openai_function_def = aci.functions.get_definition("GITHUB__GET_REPOSITORY")
        parameters = {
            "path": {
                "owner": owner,
                "repo": repo
            }
        }

        # get linked_account_owner_id from environment variable
        linked_account_owner_id = os.environ.get('LINKED_ACCOUNT_OWNER_ID')
        if not linked_account_owner_id:
            raise ValueError("LINKED_ACCOUNT_OWNER_ID environment variable is not set")

        try:
            result = aci.handle_function_call(
                openai_function_def["function"]["name"],
                parameters,
                linked_account_owner_id
            )
            return result
        except Exception as e:
            raise ToolHardError(f"Failed to execute ACI GitHub tool: {e}") from e
        
        