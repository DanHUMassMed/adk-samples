
"""Academic_newresearch_agent for finding new research lines"""

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from . import prompt

import litellm
litellm._turn_on_debug()

MODEL=LiteLlm(model="openai/gpt-oss:20b",
            api_base="http://localhost:11434/v1", 
            api_key="my_api_key")

academic_newresearch_agent = Agent(
    model=MODEL,
    name="academic_newresearch_agent",
    instruction=prompt.ACADEMIC_NEWRESEARCH_PROMPT,
)
