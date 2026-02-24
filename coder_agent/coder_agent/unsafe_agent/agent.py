from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.code_executors import UnsafeLocalCodeExecutor

# 2. Configure the LiteLLM Model
model = LiteLlm(model="openai/gpt-oss:20b",
                api_base="http://localhost:11434/v1", 
                api_key="my_api_key")

# 3. Create the Agent
root_agent = Agent(
    name="code_assistant",
    model=model,
    code_executor=UnsafeLocalCodeExecutor(),
    instruction="You are a coder. Create Python code to verify your math."
)
