# Currency Agent Sample

This project demonstrates an Agent-to-Agent (A2A) compatible Currency Agent that utilizes the Model Context Protocol (MCP) to fetch real-time exchange rates.

## Components

1.  **Exchange MCP Server (`exchange_mcp/server.py`)**: A FastMCP server that provides a `get_exchange_rate` tool. It fetches data from the [Frankfurter API](https://api.frankfurter.app/).
2.  **Currency Agent (`currency_agent/agent.py`)**: A Google ADK `LlmAgent` that connects to the MCP server. It is exposed as an A2A endpoint.
3.  **Clients**:
    *   `exchange_mcp/test_server.py`: Directly tests the MCP server.
    *   `a2a_client/test_client.py`: Tests the A2A Currency Agent interface.

## Prerequisites

*   Python 3.10+
*   `uv` package manager
*   A Google Cloud Project with the Gemini API enabled (for the agent).

## Setup

1.  **Install dependencies**:
    ```bash
    uv sync
    source .venv/bin/activate
    ```

2.  **Environment Variables**:
    Ensure you have your environment variables set up (e.g., `GOOGLE_API_KEY` for the LLM). Create a `.env` file if needed.

## Running the Application

You need to run the MCP server and the Agent simultaneously. Open two terminal windows.

### 1. Start the MCP Server

In the first terminal:
```bash
uv run exchange_mcp/server.py
```
This starts the MCP server on port 8080.

### 2. Start the Currency Agent

In the second terminal:
```bash
uv run uvicorn currency_agent.agent:a2a_app --host localhost --port 10000
```
This starts the Currency Agent on port 10000.

## Testing

### Test the MCP Server (Directly)

Ensure the MCP server is running, then run:
```bash
uv run exchange_mcp/test_server.py
```

### Test the Currency Agent (A2A Client)

Ensure both the MCP server and the Currency Agent are running, then run:
```bash
uv run a2a_client/test_client.py
```
This script runs single-turn and multi-turn conversation tests against the agent.
