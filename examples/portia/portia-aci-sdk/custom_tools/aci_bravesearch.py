from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext, ToolHardError

from aci import ACI
import os


class BraveSearchToolSchema(BaseModel):
    """Schema defining the inputs for the BraveSearchTool."""

    query: str = Field(..., 
        description="The query to search for",
    )


class BraveSearchTool(Tool):
    """Searches the web for information."""

    id: str = "BRAVE_SEARCH__WEB_SEARCH"
    name: str = "BRAVE_SEARCH__WEB_SEARCH"
    description: str = "Searches the web for information"
    args_schema: type[BaseModel] = BraveSearchToolSchema
    output_schema: tuple[str, str] = ("str", "A string indicating the search results")

    def run(self, _: ToolRunContext, query: str) -> str:
        """Run the BraveSearchTool."""
        aci = ACI()
        openai_function_def=aci.functions.get_definition("BRAVE_SEARCH__WEB_SEARCH")
        parameters = {
            "query": {
                "q": query,
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
            raise ToolHardError(f"Failed to execute ACI GitHub tool: {e}")

        
        