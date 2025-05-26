from pathlib import Path
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext

from aci import ACI


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

        result = aci.handle_function_call(
            openai_function_def["function"]["name"],
            parameters,
            linked_account_owner_id="<your-linked-account-owner-id>",
        )
        return result
        
        