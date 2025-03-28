# Aipolabs Agents

AI agents built with ACI.dev along with many examples of how to use ACI.dev with
different LLMs and agent frameworks such as langchain, CrewAI, Llama Index, etc.

## Examples

The [examples](./examples/) directory contains example implementations demonstrating different approaches to using the Aipolabs ACI Python SDK with LLM agents.

### 1. Agent with Pre-planned Functions

[agent_with_pre_planned_tools.py](./examples/agent_with_pre_planned_tools.py)

This example demonstrates the simplest way to use Aipolabs ACI functions with an LLM agent. It:

- Pre-selects specific functions by developers before the conversation

### 2. Agent with Dynamic Function Discovery and Fixed Tools

[agent_with_dynamic_function_discovery_and_fixed_tools.py](./examples/agent_with_dynamic_function_discovery_and_fixed_tools.py)

- Use all 4 meta functions (ACI_SEARCH_APPS, ACI_SEARCH_FUNCTIONS, ACI_GET_FUNCTION_DEFINITION, ACI_EXECUTE_FUNCTION)

### 3. Agent with Dynamic Function Discovery and Dynamic Tools

[agent_with_dynamic_function_discovery_and_dynamic_tools.py](./examples/agent_with_dynamic_function_discovery_and_dynamic_tools.py)

- Use 3 meta functions (ACI_SEARCH_APPS, ACI_SEARCH_FUNCTIONS, ACI_GET_FUNCTION_DEFINITION)

### Examples with different LLMs and Frameworks

- Anthropic: [anthropic_with_pre_planned_tool.py](./examples/llms/anthropic_with_pre_planned_tool.py)
- CrewAI: [crewai_with_pre_planned_tool.py](./examples/frameworks/crewai/crewai_with_pre_planned_tool.py)
- LangChain: [chatopenai_with_pre_planed_tool.py](./examples/frameworks/langchain/chatopenai_with_pre_planed_tool.py)
- Llama Index: [llamaindex_with_pre_planned_tool.py](./examples/frameworks/llamaindex/llamaindex_with_pre_planned_tool.py)

## Key Differences Between example 2 and 3

- In example 2, the retrieved function definition (e.g., `BRAVE_SEARCH__WEB_SEARCH`) is fed directly to the LLM as chat text, and the LLM generates function arguments based on the function definition and then generates a `ACI_EXECUTE_FUNCTION` function call.

- In example 3, the retrieved function definition is stored in the `tools_retrieved` list, and can be dynamically appended to or removed from the LLM's tool list. The LLM will generate a direct function call that matches the retrieved function. (e.g., `BRAVE_SEARCH__WEB_SEARCH`)

## Running the examples

The examples are runnable, for a quick setup:

- Clone the whole repository and install dependencies `uv sync`
- Set your OpenAI API key and/or Anthropic API key (set as `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` in your environment). See [.env.example](.env.example).
- Set your Aipolabs ACI API key (set as `AIPOLABS_ACI_API_KEY` in your environment)
- Configure the app the example uses (e.g `BRAVE_SEARCH`) in the [Aipolabs ACI platform](https://platform.aci.dev)
- Allow the Apps (e.g., `BRAVE_SEARCH`) to be used by your `agent` in the [Aipolabs ACI platform](https://platform.aci.dev)
- Link an  account for the app you use on the [Aipolabs ACI platform](https://platform.aci.dev). If the app requires an API key (e.g. `BRAVE_SEARCH`) then you need to get the api key from that app (e.g. [brave](https://brave.com/search/api/)). If the app use OAuth2 (e.g. `GITHUB`), you need to complete the OAuth2 flow on
  the ACI.dev platform when linking your account.
- Set the `LINKED_ACCOUNT_OWNER_ID` environment variable to your owner id of the linked account you just created.
- Run any example: `uv run python examples/agent_with_pre_planned_tools.py`
- You might need to repeat the above steps for other examples if they use different apps.
