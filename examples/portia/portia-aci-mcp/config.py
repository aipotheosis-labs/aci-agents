import os
from dotenv import load_dotenv
from portia import Config, LLMProvider, McpToolRegistry, DefaultToolRegistry

load_dotenv() 

#configure aci api key and check for missing exceptions
aci_api_key_value = os.getenv("ACI_API_KEY")
google_api_key_value = os.getenv("GOOGLE_API_KEY")
process_env = os.environ.copy()
if aci_api_key_value:
    process_env["ACI_API_KEY"] = aci_api_key_value
else:
    print("Warning: ACI_API_KEY was not found in the environment. The aci-mcp tool might fail.")

if not google_api_key_value:
    raise ValueError("GOOGLE_API_KEY is not set")


# config for gemini api
config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE,
    google_api_key=google_api_key_value,
    default_model="google/gemini-2.0-flash",
)

# config for mcp tools via portia's mcp tool registry, refer to env.example for setup
mcp_registry = McpToolRegistry.from_stdio_connection(
    server_name="aci-apps-stdio",
    command="uvx",
    args=[
        "aci-mcp", "apps-server",
        "--apps=BRAVE,GITHUB,GMAIL",
        # "--linked-account-owner-id= <your-linked-account-owner-id> ", # you can setup your linked acc owner ID at - https://platform.aci.dev/apps
    ],
    env=process_env
)

#  combine ACI's MCP tools with Portia's built-in tools
tool_registry = mcp_registry + DefaultToolRegistry(config)
