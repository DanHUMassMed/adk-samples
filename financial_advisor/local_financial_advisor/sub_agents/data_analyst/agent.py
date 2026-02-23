
"""data_analyst_agent for finding information using duckduckgo search"""

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import duckduckgo_search_tool

from . import prompt

MODEL=LiteLlm(model="openai/gpt-oss:20b",
            api_base="http://localhost:11434/v1", 
            api_key="my_api_key")

data_analyst_agent = Agent(
    model=MODEL,
    name="data_analyst_agent",
    instruction=prompt.DATA_ANALYST_PROMPT,
    output_key="market_data_analysis_output",
    tools=[duckduckgo_search_tool],
)
