from pathlib import Path
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext

from aci import ACI


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

        result = aci.handle_function_call(
            openai_function_def["function"]["name"],
            parameters,
            linked_account_owner_id="<your-linked-account-owner-id>",
        )
        return result
        
        