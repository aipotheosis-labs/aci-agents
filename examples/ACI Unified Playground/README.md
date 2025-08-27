# ACI Unified Playground

Interactive playground showcasing ACI.dev's Unified MCP Server with 600+ tools for memory management, web search, email operations, database queries, and multi-tool workflows.

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- ACI.dev account with API key
- Google API key for Gemini model

### Installation

1. **Clone and install dependencies:**

```bash
git clone <repository-url>
cd aci-unified-playground
pip install -r requirements.txt
cd frontend && npm install
```

2. **Configuration - Choose one method:**

**Method A: Create .env file**

```env
ACI_API_KEY=your_aci_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
LINKED_ACCOUNT_OWNER_ID=your_account_id
```

**Method B: Use web interface**

- Start the application (step 3)
- Enter credentials in the Configuration section in the sidebar
- Click "Save Configuration"
- Restart the server

3. **Run the application:**

```bash
# Terminal 1: Start backend
python memory_agent.py

# Terminal 2: Start frontend
cd frontend && npm start
```

4. **Access the playground:**
   Open http://localhost:3000 in your browser

## Features

### Tool Categories

- **Memory Management** - Store and retrieve personal information
- **Web Search** - Research current information and trends
- **Email Operations** - Manage email communications
- **Database Queries** - Connect to and query databases
- **Multi-tool Workflows** - Combine multiple tools for automation

### Usage

1. Click pre-built prompts in the sidebar for quick examples
2. Type custom requests in natural language
3. AI automatically discovers and uses appropriate tools
4. View tool execution details in real-time

## CLI Version

For command-line usage:

```bash
python object_agent.py
```

## Configuration Options

Optional environment variables for app filtering:

```env
# Include only specific apps
ACI_ALLOWED_APPS=app1,app2,app3

# Exclude specific apps
ACI_EXCLUDED_APPS=app4,app5
```
