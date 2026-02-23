import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

#glm-4.7-flash:q8_0 
#gpt-oss:20b

MODEL = LiteLlm(model="openai/gpt-oss:20b",
                  api_base="http://localhost:11434/v1", 
                  api_key="no_ollama_key_needed")

root_agent = Agent(
    name="searngx_search_agent",
    model=MODEL,
    description=(
        "Agent can help users search for information on the web."
    ),
    instruction=(
        "You are an search agent who can help users search for information on the web. you always provide links in your response."
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
