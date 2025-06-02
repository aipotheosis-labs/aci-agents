"""Registry containing my custom tools."""

from portia import InMemoryToolRegistry
from custom_tools.aci_bravesearch import BraveSearchTool
from custom_tools.aci_github import GithubGetRepositoryTool
from custom_tools.aci_gmail import GmailSendEmailTool

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        BraveSearchTool(),
        GithubGetRepositoryTool(),
        GmailSendEmailTool(),
    ],
)