# SearXNG MCP Server

This directory contains the **Model Context Protocol (MCP)** server implementation for the SearXNG search agent. It acts as a bridge between the AI Agent and a live [SearXNG](https://docs.searxng.org/) search engine instance.

## What this code does

1.  **Exposes a Search Tool**: It uses the `mcp` library (specifically `FastMCP`) to define a tool named `search`.
2.  **Connects to SearXNG**: The `SearXNGConnector` class (`connector.py`) handles HTTP communication with a SearXNG instance (defaulting to `http://localhost:32768`).
3.  **Formats Results**: It processes the JSON response from SearXNG and returns a structured list of results, making it easy for an LLM to consume web search data.

## Manual Testing with MCP Inspector

You can interactively test the MCP server tools without running the full agent using the **MCP Inspector**.

### Prerequisites

*   Ensure you have a running instance of SearXNG (default: `http://localhost:32768`).
*   Ensure dependencies are installed:
    ```bash
    uv sync
    ```

### Running the Inspector

Run the following command from the project root:

```bash
uv run mcp dev searxng_mcp/server.py
```

### Using the Inspector

1.  The command will launch a local web interface (typically at `http://localhost:5173` or similar) and open it in your browser.
2.  Verify that the **"searxng_search"** server is connected.
3.  Navigate to the **Tools** tab.
4.  Select the `search` tool.
5.  Enter test arguments:
    *   `query`: "Python 3.13 features"
    *   `max_results`: 3
6.  Click **Run Tool**.
7.  Inspect the JSON output to verify the integration with SearXNG is working correctly.