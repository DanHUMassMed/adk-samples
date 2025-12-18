# SearXNG Search Agent

This project demonstrates a Google ADK Agent that uses the **Model Context Protocol (MCP)** to perform web searches via a **SearXNG** instance.

## What this code does

1.  **Agent Definition (`searxng_search_agent/agent.py`)**: 
    -   Defines an AI agent using the `google-adk` library.
    -   The agent is powered by a `LiteLlm` configuration, enabling it to connect to a local LLM service (e.g., Ollama) at `http://localhost:11434/v1`.
    -   It is configured with an **MCP Toolset** that connects to a local MCP server.

2.  **MCP Server (`searxng_mcp/server.py`)**:
    -   Implements a FastMCP server that exposes a `search` tool.
    -   This server runs as a subprocess controlled by the agent.

3.  **SearXNG Connector (`searxng_mcp/connector.py`)**:
    -   Handles the HTTP communication with a SearXNG search engine instance.
    -   By default, it attempts to connect to `http://localhost:32768`.

## Prerequisites

Before running the agent, ensure you have the following:

1.  **Python Environment**: The project uses `uv` for dependency management.
2.  **SearXNG Instance**: You need a running instance of [SearXNG](https://docs.searxng.org/).
    -   **Important**: The default configuration expects SearXNG to be running at **`http://localhost:32768`**.
    -   If your instance is on a different port (e.g., 8080), open `searxng_mcp/connector.py` and update the `base_url` in the `__init__` method.

## How to Run

1.  **Install Dependencies**:
    Ensure your virtual environment is synced:
    ```bash
    uv sync
    ```

2.  **Start the Agent**:
    Use the ADK CLI to start the web interface:
    ```bash
    adk web
    ```
    *(Or `uv run adk web` if adk is not in your global path)*

3.  **Use the Agent**:
    -   Open your browser to the URL displayed in the terminal (typically `http://127.0.0.1:8000/dev-ui/`).
    -   Select the agent (e.g., `searngx_search_agent`) if prompted.
    -   Enter a query like: *"Find the latest release notes for Python."*
    -   The agent will use the MCP tool to query your SearXNG instance and summarize the results.