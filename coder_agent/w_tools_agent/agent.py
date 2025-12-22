from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# 1. Define a custom "Code Runner" tool
from .tools import local_python_executor

# 2. Configure the LiteLLM Model
model = LiteLlm(model="openai/gpt-oss:20b",
                api_base="http://localhost:11434/v1", 
                api_key="my_api_key")

# 3. Create the Agent
root_agent = Agent(
    name="code_assistant",
    model=model,
    tools=[local_python_executor], # Pass your custom executor here
    instruction="You are a coder. Use local_python_executor to verify your math."
)
