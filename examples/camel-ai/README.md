# CAMEL AI with Direct ACI Toolkit Integration

This example demonstrates how to integrate ACI.dev directly with CAMEL AI agents using the ACI Toolkit.

## 🚀 Features

- **Direct ACI Toolkit Integration**: Simple and straightforward integration with ACI tools
- **Multiple AI Tools**: Access to BRAVE_SEARCH, GITHUB, and ARXIV through ACI
- **Gemini Model Integration**: Uses Google's Gemini 2.0 Flash model for AI responses
- **Rich Console Output**: Beautiful terminal output with progress indicators
- **Error Handling**: Comprehensive error handling with detailed information

## 📁 Project Structure

```
.
├── aci_toolkit_camel.py    # Direct ACI Toolkit integration example
├── README.md               # This file
└── env.example            # Environment variables template
```

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- ACI API access
- Google Gemini API access

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/aipotheosis-labs/aci-agents
   cd aci-agents/examples/camel-ai/
   ```

2. **Install dependencies**:

   ```bash
   uv pip install camel-ai python-dotenv rich
   ```

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

## 🎯 Usage

Run the direct ACI toolkit integration example:

```bash
python aci_toolkit_camel.py
```

**How it works**:

1. **Initialization**: Sets up the ACI toolkit with your linked account
2. **Tool Loading**: Automatically loads available ACI tools (BRAVE_SEARCH, GITHUB, ARXIV)
3. **Model Setup**: Configures Google Gemini 2.0 Flash model
4. **Agent Creation**: Creates a CAMEL AI agent with access to ACI tools
5. **Interactive Query**: Prompts for user input and processes the query
6. **Tool Execution**: Automatically calls relevant tools based on the query
7. **Response Display**: Shows the agent's response with rich formatting

**Example Queries**:

- "Search for recent papers about large language models"
- "Find GitHub repositories related to machine learning"
- "What are the latest developments in AI research?"

## 🔧 Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set in your `.env` file
2. **Network Issues**: Check internet connectivity for API calls
3. **Model Access**: Please verify that your Google API key is valid
4. **ACI Permissions**: Verify your ACI API key has proper permissions

### Debug Information

The script includes comprehensive error handling and displays:

- Tool loading status
- Raw response details
- Message processing information
- Detailed error traces when issues occur

## 📚 Code Structure

The main script (`aci_toolkit_camel.py`) follows this flow:

1. **Environment Setup**: Loads environment variables and configurations
2. **ACI Toolkit Initialization**: Creates ACI toolkit instance with linked account
3. **Model Configuration**: Sets up Gemini model with specific parameters
4. **Agent Creation**: Combines model and tools into a CAMEL AI agent
5. **Query Processing**: Handles user input and agent response
6. **Output Display**: Shows results with rich console formatting

## 🔗 Links

- [CAMEL AI](https://github.com/camel-ai/camel) - Multi-agent framework
- [ACI Platform](https://platform.aci.dev/) - AI Compute Infrastructure
- [Google AI Studio](https://aistudio.google.com/) - Gemini API access
