
from dataclasses import dataclass
from google.adk.models.lite_llm import LiteLlm

@dataclass
class ResearchConfiguration:
    """Configuration for research-related models and parameters.

    Attributes:
        critic_model Model for evaluation tasks.
        worker_model Model for working/generation tasks.
        max_search_iterations (int): Maximum search iterations allowed.
    """

    MODEL = LiteLlm(model="openai/gpt-oss:20b",
                    api_base="http://localhost:11434/v1", 
                    api_key="no_ollama_key_needed")

    critic_model= MODEL
    worker_model= MODEL
    max_search_iterations: int = 5


config = ResearchConfiguration()
