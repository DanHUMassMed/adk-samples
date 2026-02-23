
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters
from . import prompt

import litellm
litellm._turn_on_debug()

MODEL=LiteLlm(model="openai/gpt-oss:20b",
            api_base="http://localhost:11434/v1", 
            api_key="my_api_key")



academic_websearch_agent = Agent(
    name="academic_websearch_agent",
    model=MODEL,
    instruction=prompt.ACADEMIC_WEBSEARCH_PROMPT,
    output_key="recent_citing_papers",
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




#MODEL = "gemini-2.5-flash"

# academic_websearch_agent = Agent(
#     model=MODEL,
#     name="academic_websearch_agent",
#     instruction=prompt.ACADEMIC_WEBSEARCH_PROMPT,
#     output_key="recent_citing_papers",
#     tools=[google_search],
# )
