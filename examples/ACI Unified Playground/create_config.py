import os
import json
from dotenv import load_dotenv


def create_config():
    """Create MCP config for Unified MCP Server with dynamic function discovery"""
    load_dotenv()

    aci_api_key = os.getenv("ACI_API_KEY")
    if not aci_api_key:
        raise ValueError("ACI_API_KEY environment variable is required")

    config = {
        "mcpServers": {
            "aci_unified": {
                "command": "aci-mcp",
                "args": [
                    "unified-server",
                    "--linked-account-owner-id",
                    "your_linked_acc_owner_id",
                    "--allowed-apps-only",
                ],
                "env": {"ACI_API_KEY": aci_api_key},
            }
        }
    }

    # Write to config.json
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✓ Unified MCP Config created successfully with API key")
    return config


if __name__ == "__main__":
    create_config()
