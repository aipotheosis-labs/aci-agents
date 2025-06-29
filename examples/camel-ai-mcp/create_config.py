import os
import json
import sys
from dotenv import load_dotenv


def create_config():
    """Create MCP config with proper environment variable substitution"""
    load_dotenv()

    aci_api_key = os.getenv("ACI_API_KEY")
    linked_account_owner_id = os.getenv("LINKED_ACCOUNT_OWNER_ID")
    if not aci_api_key:
        raise ValueError("ACI_API_KEY environment variable is required")
    if not linked_account_owner_id:
        raise ValueError("LINKED_ACCOUNT_OWNER_ID environment variable is required")

    config = {
        "mcpServers": {
            "aci_apps": {
                "command": sys.executable,
                "args": [
                    "-m",
                    "aci_mcp",
                    "apps-server",
                    "--apps=BRAVE_SEARCH,GITHUB,ARXIV",
                    "--linked-account-owner-id",
                    linked_account_owner_id,
                ],
                "env": {"ACI_API_KEY": aci_api_key},
            }
        }
    }

    # Write to config.json
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✓ Config created successfully with API key")
    return config


if __name__ == "__main__":
    create_config()
