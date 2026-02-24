from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.code_executors.container_code_executor import ContainerCodeExecutor
# 1️⃣ Create container executor
local_python_executor = ContainerCodeExecutor(
    image="python:3.11-slim",  # Docker image
    timeout=10,                # max execution time
    memory_limit="256m",       # memory cap
    cpu_limit=1.0              # cpu limit
)

MODEL=LiteLlm(model="openai/gpt-oss:20b",
            api_base="http://localhost:11434/v1", 
            api_key="my_api_key")
            
MODEL="gemini-3-flash-preview"

# 2️⃣ Define agent with code_executor
coder_agent = Agent(
    model=MODEL,
    name="coder_agent",
    instruction="You are a coder. To verify math, you must output your python code in a markdown block starting with ```python and ending with ```. Do not use function calls.",
    code_executor=local_python_executor,
)

root_agent = coder_agent