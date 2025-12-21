
from .prompts import return_instructions_root
from .tools import ask_chromadb
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from openinference.instrumentation import using_session
import uuid
from .tracing import instrument_adk_with_phoenix

# Run Phoenix UI: phoenix serve
_ = instrument_adk_with_phoenix()

with using_session(session_id=uuid.uuid4()):
    root_agent = Agent(
        name="ask_rag_agent",
        model=LiteLlm(model="openai/gpt-oss:20b",
                    api_base="http://localhost:11434/v1", 
                api_key="my_api_key"),
    description="A simple agent that can answer questions based on documents.",
    instruction=return_instructions_root(),
    tools=[ask_chromadb],
)

print("✅ Root Agent defined.")


