# Aipolabs Agents

AI agents built with ACI.dev along with many examples of how to use ACI.dev with
different LLMs and agent frameworks such as langchain, CrewAI, Llama Index, etc.


## Patterns

There are **2 main patterns** for building agents with Aipolabs ACI, regardless of the LLM or framework used.  
The second pattern includes **2 sub-patterns** based on how tools are discovered and used.


### 1. Agent with Pre-planned Tools (Static Tools)

- **Suitable for**: When the tools needed are limited and known beforehand  
- **Example**: [`agent_with_pre_planned_tools.py`](./examples/openai/agent_with_pre_planned_tools.py)


### 2. Agent with Dynamic Tool Discovery and Execution

- **Suitable for**: When many tools are needed and/or tools are not known ahead of time
- **Example 2.1**: [`agent_with_dynamic_tool_discovery_pattern_1.py`](./examples/openai/agent_with_dynamic_tool_discovery_pattern_1.py)
- **Example 2.2**: [`agent_with_dynamic_tool_discovery_pattern_2.py`](./examples/openai/agent_with_dynamic_tool_discovery_pattern_2.py)



#### 2.1 Tool List Expansion Approach

With this approach, you:
- Use `ACI_SEARCH_FUNCTIONS` meta function (tool):  
- Search for relevant functions across all apps
- Add discovered tools directly to the LLM's tool list
- Allow the LLM to invoke these discovered tools directly by name

**Key implementation points:**
- Maintain a `tools_retrieved` list that dynamically adds/removes tools as they are discovered or abandoned
- When `ACI_SEARCH_FUNCTIONS` returns functions (tools), add to this list
- Pass both `ACI_SEARCH_FUNCTIONS` and discovered functions (tools) to the LLM in each request
- The LLM calls discovered tools by name (e.g., `BRAVE_SEARCH__WEB_SEARCH`)


#### 2.2 Tool Definition as Text Context Approach (Less Reliable)

With this approach, you:

- Use `ACI_SEARCH_FUNCTIONS` and `ACI_EXECUTE_FUNCTION` meta functions (tools)
- Use `ACI_SEARCH_FUNCTIONS` to retrieve tool definitions
- Present those definitions to the LLM as **text content** instead of adding them to the LLM's tool list
- The LLM uses `ACI_EXECUTE_FUNCTION` to execute these tools **indirectly**
- Note: This approach has lower function calling accuracy compared to the Tool List Expansion Approach due to the tools attached as text content instead of being added to the LLM's tool list

**Key implementation points:**
- Only include meta functions (tools) in the LLM's tool list
- Share tool definitions as chat content
- The LLM reads the tool definition to generate appropriate arguments
- The LLM calls `ACI_EXECUTE_FUNCTION` with the tool name and arguments


### 🔁 **Execution Flow Comparison**

| Pattern | Approach | Flow |
|--------|----------|------|
| **1** | Pre-planned tools | `Define Tools in tools list → Direct Tool Call` |
| **2.1** | Tool List Expansion | `Search → Get Tool Definition → Add to Tools → Direct Tool Call` |
| **2.2** | Text Context Execution | `Search → Get Tool Definition → Add to Text Context → Call via Meta Function` |


## Running the examples

The examples are runnable, for a quick setup:

- Clone the whole repository and install dependencies `uv sync`
- Set your OpenAI API key and/or Anthropic API key (set as `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` in your environment). See [.env.example](.env.example).
- Set your Aipolabs ACI API key (set as `ACI_API_KEY` in your environment)
- Configure the app the example uses (e.g `BRAVE_SEARCH`) in the [Aipolabs ACI platform](https://platform.aci.dev)
- Allow the Apps (e.g., `BRAVE_SEARCH`) to be used by your `agent` in the [Aipolabs ACI platform](https://platform.aci.dev)
- Link an  account for the app you use on the [Aipolabs ACI platform](https://platform.aci.dev). If the app requires an API key (e.g. `BRAVE_SEARCH`) then you need to get the api key from that app (e.g. [brave](https://brave.com/search/api/)). If the app use OAuth2 (e.g. `GITHUB`), you need to complete the OAuth2 flow on
  the ACI.dev platform when linking your account.
- Set the `LINKED_ACCOUNT_OWNER_ID` environment variable to your owner id of the linked account you just created.
- Run any example: `uv run python examples/agent_with_pre_planned_tools.py`
- You might need to repeat the above steps for other examples if they use different apps.
