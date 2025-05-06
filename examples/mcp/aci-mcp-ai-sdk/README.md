# ACI MCP AI SDK Example

This example demonstrates how to use the ACI MCP with Vercel's AI SDK including both [Unified MCP Server](https://www.aci.dev/docs/mcp-servers/unified-server) and [Apps MCP Server](https://www.aci.dev/docs/mcp-servers/apps-server). 

## Prerequisites

- Node.js (v16 or higher)
- pnpm (v10.6.1 or higher)
- ACI API Key
- OpenAI API Key

## Setup

1. Install dependencies:
```bash
pnpm install
```

2. Create a `.env` file in the project root with the following variables:
```env
ACI_API_KEY=your_aci_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Example

To run the example:

```bash
pnpm start
```

This will:
1. Initialize a unified MCP server
2. Demonstrate tool usage with the unified server
3. Initialize an apps MCP server with Brave Search integration
4. Demonstrate tool usage with the apps server

## Project Structure

- `index.ts`: Main application file that demonstrates MCP server usage
- `package.json`: Project dependencies and scripts
- `tsconfig.json`: TypeScript configuration
- `.env`: Environment variables

## Dependencies

- `@ai-sdk/openai`: OpenAI integration
- `ai`: Core AI functionality
- `dotenv`: Environment variable management
- `ts-node`: TypeScript execution
- `typescript`: TypeScript support

## Notes

- The example uses GPT-4 as the AI model
- The apps server is configured with Brave Search integration
