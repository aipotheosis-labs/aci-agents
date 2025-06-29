# CAMEL AI with MCP Server Integration

This example demonstrates how to integrate ACI.dev with CAMEL AI agents using the Model Context Protocol (MCP) server approach.

## 🚀 Features

- **MCP Protocol Integration**: Uses Model Context Protocol for modular tool integration
- **Automatic Configuration**: Generates MCP server configuration automatically
- **Async Processing**: Full asynchronous support for better performance
- **Multiple AI Tools**: Access to BRAVE_SEARCH, GITHUB, and ARXIV through ACI MCP server
- **Gemini Model Integration**: Uses Google's Gemini 2.0 Flash model for AI responses
- **Tool Output Summarization**: Intelligent summarization of tool call results
- **Interactive Experience**: User-friendly input prompts and rich console output
- **Modular Architecture**: Extensible design supporting multiple MCP servers

## 📁 Project Structure

```
.
├── aci_mcp_camel.py       # MCP server integration example
├── create_config.py       # MCP configuration generator
├── README.md              # This file
└── env.example           # Environment variables template
```

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- ACI API access
- Google Gemini API access
- MCP server capabilities

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/aipotheosis-labs/aci-agents
   cd aci-agents/examples/camel-ai-mcp/
   ```

2. **Install dependencies**:

   ```bash
   # using pip
   pip install camel-ai python-dotenv rich aci-mcp
   ```

   **Note**: The `aci-mcp` package provides the MCP server as a Python module that can be executed with `python -m aci_mcp`.

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

- `ACI_API_KEY`: Your ACI API key
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `LINKED_ACCOUNT_OWNER_ID`: Your linked account owner ID

You can get these from:

- **ACI API Key**: Configure your apps and get your key at [ACI Platform](https://platform.aci.dev/apps)
- **Google API Key**: Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### MCP Configuration

The `create_config.py` script automatically generates the necessary `config.json` file for MCP server connections. This configuration specifies:

- **Server Command**: Uses Python module execution (`python -m aci_mcp`)
- **Available Apps**: BRAVE_SEARCH, GITHUB, and ARXIV tools
- **Authentication**: Passes ACI_API_KEY through environment variables
- **Account Linking**: Uses your LINKED_ACCOUNT_OWNER_ID for tool access

## 🎯 Usage

### Quick Start

Run the MCP server integration example:

```bash
python aci_mcp_camel.py
```

**How it works**:

1. **Configuration Generation**: Automatically creates MCP server configuration
2. **MCP Connection**: Establishes connection to ACI MCP server
3. **Tool Discovery**: Discovers and loads available tools from MCP server
4. **Model Setup**: Configures Google Gemini 2.0 Flash model
5. **Agent Creation**: Creates CAMEL AI agent with MCP-provided tools
6. **Interactive Query**: Prompts for user input and processes requests
7. **Async Processing**: Handles tool calls asynchronously for better performance
8. **Result Summarization**: Summarizes tool outputs into natural language responses
9. **Clean Disconnection**: Properly closes MCP server connections

**Example Queries**:

- "Search for recent developments in quantum computing"
- "Find GitHub repositories about neural networks created this year"
- "What are the latest arXiv papers on transformer architectures?"

## 🔧 Troubleshooting

### Common Issues

1. **MCP Server Connection**: Ensure `aci-mcp` is properly installed via `pip install aci-mcp`
2. **Configuration Issues**: Check if `config.json` is generated correctly by running `python create_config.py`
3. **Missing API Keys**: Verify all environment variables are set in `.env` file
4. **Module Import Error**: Ensure `aci_mcp` module is available in your Python environment
5. **Permission Issues**: Ensure proper file creation permissions for config files
6. **Network Issues**: Check connectivity to ACI services and internet access

## 📚 Code Structure

### Main Components

1. **`aci_mcp_camel.py`**: Primary integration script

   - Async main function
   - MCP toolkit initialization
   - Agent setup and execution
   - Tool output summarization

2. **`create_config.py`**: Configuration generator
   - Reads ACI_API_KEY and LINKED_ACCOUNT_OWNER_ID from environment
   - Generates config.json with Python module-based MCP server setup
   - Configures aci-mcp apps-server with specific tools (BRAVE_SEARCH, GITHUB, ARXIV)
   - Uses `sys.executable` to ensure correct Python interpreter

### Key Functions

- **`summarize_tool_outputs()`**: Processes and summarizes tool call results
- **`main()`**: Primary async execution function
- **`create_config()`**: Generates MCP server configuration

## 🎛️ Customization

### Model Configuration

Modify the model setup in `aci_mcp_camel.py`:

```python
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.0-flash-001",  # Change model version
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_config_dict={
        "temperature": 0.7,  # Adjust creativity
        "max_tokens": 8000,  # Modify response length
    },
)
```

### System Message

Customize the agent's behavior:

```python
system_message = BaseMessage.make_assistant_message(
    role_name="Assistant",
    content="Your custom system prompt here",
)
```

### MCP Configuration Customization

To customize which tools are available, modify `create_config.py`:

```python
# Change the apps parameter to include/exclude tools
"--apps=BRAVE_SEARCH,GITHUB,ARXIV",  # Add or remove tools as needed

# Available tools: BRAVE_SEARCH, GITHUB, ARXIV, GMAIL (if configured)
```

Or create a custom config.json manually:

```json
{
  "mcpServers": {
    "aci_apps": {
      "command": "python",
      "args": [
        "-m",
        "aci_mcp",
        "apps-server",
        "--apps=BRAVE_SEARCH,GITHUB",
        "--linked-account-owner-id",
        "your_id"
      ],
      "env": {
        "ACI_API_KEY": "your_api_key"
      }
    }
  }
}
```

## 🔗 Links

- [CAMEL AI](https://github.com/camel-ai/camel) - Multi-agent framework
- [ACI Platform](https://platform.aci.dev/) - AI Compute Infrastructure
- [MCP Protocol](https://modelcontextprotocol.io/) - Model Context Protocol specification
- [Google AI Studio](https://aistudio.google.com/) - Gemini API access
