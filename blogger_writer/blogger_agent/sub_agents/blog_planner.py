# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent, LoopAgent


from ..config import config
from ..tools import duckduckgo_search_tool
from ..agent_utils import suppress_output_callback
from ..validation_checkers import OutlineValidationChecker

blog_planner = Agent(
    model=LiteLlm(model=config.worker_model,
                    api_base="http://localhost:11434/v1", 
                api_key="my_api_key"),
    name="blog_planner",
    description="Generates a blog post outline.",
    instruction="""
    You are a technical content strategist. Your job is to create a blog post outline.
    The outline should be well-structured and easy to follow.
    It should include a title, an introduction, a main body with several sections, and a conclusion.
    If a codebase is provided, the outline should include sections for code snippets and technical deep dives.
    The codebase context will be available in the `codebase_context` state key.
    Use the information in the `codebase_context` to generate a specific and accurate outline.
    Use DuckDuckGo Search to find relevant information and examples to support your writing.
    Your final output should be a blog post outline in Markdown format.
    """,
    tools=[duckduckgo_search_tool],
    output_key="blog_outline",
    after_agent_callback=suppress_output_callback,
)

robust_blog_planner = LoopAgent(
    name="robust_blog_planner",
    description="A robust blog planner that retries if it fails.",
    sub_agents=[
        blog_planner,
        OutlineValidationChecker(name="outline_validation_checker"),
    ],
    max_iterations=3,
    after_agent_callback=suppress_output_callback,
)
