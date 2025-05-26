import { experimental_createMCPClient, generateText } from 'ai';
import { Experimental_StdioMCPTransport } from 'ai/mcp-stdio';
import { openai } from '@ai-sdk/openai';
import dotenv from 'dotenv';

dotenv.config();

async function main() {
  let unifiedMCPServer;
  let appsMCPServer;

  try {
    if (!process.env.ACI_API_KEY) {
      throw new Error('ACI_API_KEY is required');
    }
    if (!process.env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY is required');
    }

    console.log('Creating unified MCP server...');
    unifiedMCPServer = await experimental_createMCPClient({
      transport: new Experimental_StdioMCPTransport({
        env: {
          ACI_API_KEY: process.env.ACI_API_KEY,
        },
        command: 'uvx',
        args: ['aci-mcp', 'unified-server', '--linked-account-owner-id', 'jiwei@aipolabs.xyz'],
      }),
    });

    const unifiedMCPServerTools = await unifiedMCPServer.tools();
    console.log('Available mcp unified server tools:', unifiedMCPServerTools);

    const result1 = await generateText({
      model: openai('gpt-4'),  // Using a valid OpenAI model name
      tools: {
        ...unifiedMCPServerTools,
      },
      messages: [
        {
          role: 'user',
          content: 'hello, search tool to find papers about AI',
        },
      ],
    });
    console.log('Result 1:');
    for (const toolCall of result1.toolCalls) {
      console.log('Tool call:', toolCall);
    }

    console.log('Creating apps MCP server...');
    appsMCPServer = await experimental_createMCPClient({
      transport: new Experimental_StdioMCPTransport({
        env: {
          ACI_API_KEY: process.env.ACI_API_KEY,
        },
        command: 'uvx',
        args: ['aci-mcp', 'apps-server', '--apps','BRAVE_SEARCH', '--linked-account-owner-id', 'jiwei@aipolabs.xyz'],
      }),
    });

    const appsMCPServerTools = await appsMCPServer.tools();
    console.log('Apps MCP Server Tools:', appsMCPServerTools);
    const result2 = await generateText({
      model: openai('gpt-4'),  // Using a valid OpenAI model name
      tools: {
        ...appsMCPServerTools,
      },
      messages: [
        {
          role: 'user',
          content: 'hello, search tool to find papers about AI',
        },
      ],
    });
    console.log('Result 2:');
    for (const toolCall of result2.toolCalls) {
      console.log('Tool call:', toolCall);
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    if (unifiedMCPServer) {
      await unifiedMCPServer.close();
    }
    if (appsMCPServer) {
      await appsMCPServer.close();
    }
  }
}

main().catch(console.error);