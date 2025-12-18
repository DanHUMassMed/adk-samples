import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

root_agent = Agent(
    name="searngx_search_agent",
    model=LiteLlm(model="openai/gpt-oss:20b",
                  api_base="http://localhost:11434/v1", 
                  api_key="my_api_key"),
    description=(
        "Agent can help users search for information on the web."
    ),
    instruction=(
        "You are an search agent who can help users search for information on the web."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uv",
                    args=["run", "searxng_mcp/server.py"],
                ),
            ),
        )
    ],
)
