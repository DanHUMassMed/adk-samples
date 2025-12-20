#!/usr/bin/env python3
"""
Phenix-based local evaluation suite for the RAG agent.
Uses OpenInference / Phoenix to trace agent calls and evaluate tool usage.
"""

import pathlib
import json
import asyncio
from typing import Dict, List, Any
import pandas as pd
import uuid
from dataclasses import dataclass, asdict
from litellm.llms.custom_httpx.async_client_cleanup import close_litellm_async_clients


# OpenInference / Phoenix imports
from openinference.instrumentation import using_session

# ADK agent imports
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

# Import your RAG agent
from rag_agent.agent import root_agent

from phoenix.otel import register


# -------------------------
# Dataclass for evaluation results
# -------------------------
@dataclass
class EvaluationResult:
    score: float
    label: str
    explanation: str

    def __post_init__(self):
        # Validate types
        if not isinstance(self.score, (float, int)):
            raise TypeError(f"score must be a float or int, got {type(self.score)}")
        if not isinstance(self.label, str):
            raise TypeError(f"label must be a str, got {type(self.label)}")
        if not isinstance(self.explanation, str):
            raise TypeError(f"explanation must be a str, got {type(self.explanation)}")

        # Ensure score is in [0, 1]
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"score must be between 0 and 1, got {self.score}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for printing, logging, or DataFrame."""
        return asdict(self)


# -------------------------
# Test data loader
# -------------------------
def load_test_data() -> List[Dict]:
    """Load the conversation test data from JSON file."""
    path = pathlib.Path(__file__).parent / "data/conversation.test.1.json"
    with open(path, "r") as f:
        return json.load(f)


# -------------------------
# Call the RAG agent
# -------------------------
async def call_rag_agent(query: str) -> Dict[str, Any]:
    """Call the RAG agent and return response + tool calls."""
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )

    content = UserContent(parts=[Part(text=query)])
    response_parts = []

    for event in runner.run(user_id=session.user_id, session_id=session.id, new_message=content):
        for part in event.content.parts:
            response_parts.append(part.text)

    response_text = "\n".join(part for part in response_parts if part is not None)

    # Simple tool extraction heuristic
    tool_calls = []
    if any(keyword in response_text.lower() for keyword in [
        "according to", "based on", "source:", "[citation", "retrieved", "documentation"
    ]):
        tool_calls.append({
            "tool_name": "retrieve_rag_documentation",
            "tool_input": response_text[:100] + "..." if len(response_text) > 100 else response_text
        })

    return {"response": response_text, "tool_calls": tool_calls}


async def task_function(dataset_row: Dict) -> str:
    """Evaluate a single query in a local Phoenix experiment."""
    query = dataset_row.get("query", "")
    result = await call_rag_agent(query)

    metadata = {
        "agent_response": result["response"],
        "tool_calls": result["tool_calls"],
        "expected_tool_use": dataset_row.get("expected_tool_use", "[]"),
        "reference": dataset_row.get("reference", "")
    }
    return json.dumps(metadata)


# -------------------------
# Evaluator functions
# -------------------------
def trajectory_exact_match_evaluator(output: str, dataset_row: Dict) -> EvaluationResult:
    metadata = json.loads(output)
    actual_tool_calls = metadata.get("tool_calls", [])
    expected_tool_use = dataset_row.get("expected_tool_use", [])

    # Ensure it is a list (if it's a JSON string, parse it)
    if isinstance(expected_tool_use, str):
        expected_tool_use = json.loads(expected_tool_use)

    if len(actual_tool_calls) != len(expected_tool_use):
        return EvaluationResult(
            score=0.0,
            label="no_exact_match",
            explanation=f"Length mismatch: expected {len(expected_tool_use)}, got {len(actual_tool_calls)}"
        )

    actual_names = [tc.get("tool_name", "") for tc in actual_tool_calls]
    expected_names = [et.get("tool_name", "") for et in expected_tool_use]
    score = 1.0 if actual_names == expected_names else 0.0
    label = "exact_match" if score == 1.0 else "no_exact_match"
    explanation = f"Tool sequence match: expected {expected_names}, got {actual_names}"

    return EvaluationResult(score=score, label=label, explanation=explanation)


def trajectory_precision_evaluator(output: str, dataset_row: Dict) -> EvaluationResult:
    metadata = json.loads(output)
    actual_tool_calls = metadata.get("tool_calls", [])
    expected_tool_use = dataset_row.get("expected_tool_use", [])

    # Ensure it is a list (if it's a JSON string, parse it)
    if isinstance(expected_tool_use, str):
        expected_tool_use = json.loads(expected_tool_use)

    if not expected_tool_use:
        score = 1.0 if not actual_tool_calls else 0.0
        label = "perfect" if score == 1.0 else "unexpected_tools"
        explanation = "No tools expected" + ("" if score == 1.0 else f", but got {len(actual_tool_calls)} tools")
        return EvaluationResult(score=score, label=label, explanation=explanation)

    actual_names = set(tc.get("tool_name", "") for tc in actual_tool_calls)
    expected_names = set(et.get("tool_name", "") for et in expected_tool_use)

    if not actual_names:
        return EvaluationResult(score=0.0, label="no_tools_used", explanation="No tools used when tools were expected")

    intersection = actual_names.intersection(expected_names)
    score = len(intersection) / len(actual_names)

    if score >= 0.9:
        label = "high_precision"
    elif score >= 0.7:
        label = "medium_precision"
    else:
        label = "low_precision"

    explanation = f"Precision: {len(intersection)}/{len(actual_names)} = {score:.2f}. Expected: {sorted(expected_names)}, Used: {sorted(actual_names)}"
    return EvaluationResult(score=score, label=label, explanation=explanation)


def tool_name_match_evaluator(output: str, dataset_row: Dict) -> EvaluationResult:
    metadata = json.loads(output)
    actual_tool_calls = metadata.get("tool_calls", [])
    expected_tool_use = dataset_row.get("expected_tool_use", [])

    # Ensure it is a list (if it's a JSON string, parse it)
    if isinstance(expected_tool_use, str):
        expected_tool_use = json.loads(expected_tool_use)

    actual_tool_names = {tc.get("tool_name", "") for tc in actual_tool_calls if isinstance(tc, dict)}
    expected_tool_names = {et.get("tool_name", "") for et in expected_tool_use if isinstance(et, dict)}

    if not expected_tool_names:
        score = 1.0 if not actual_tool_names else 0.0
        label = "correct_no_tools" if score == 1.0 else "unexpected_tools"
        explanation = f"No tools expected. Got: {sorted(actual_tool_names) if actual_tool_names else 'none'}"
    else:
        intersection = actual_tool_names.intersection(expected_tool_names)
        score = len(intersection) / len(expected_tool_names)
        if score == 1.0:
            label = "perfect_match"
        elif score >= 0.7:
            label = "good_match"
        elif score > 0:
            label = "partial_match"
        else:
            label = "no_match"
        explanation = f"Tool name coverage: {len(intersection)}/{len(expected_tool_names)} = {score:.2f}. Expected: {sorted(expected_tool_names)}, Got: {sorted(actual_tool_names)}"

    return EvaluationResult(score=score, label=label, explanation=explanation)


# -------------------------
# Run experiment with Phoenix
# -------------------------
async def run_local_phoenix_experiment():
    dataset = load_test_data()

    # Register with Phoenix / OpenInference
    tracer_provider = register(project_name=f"rag_agent_eval_{uuid.uuid4()}", batch=True)

    results = []
    async with using_session(session_id=uuid.uuid4()):
        for row in dataset:
            output = await task_function(row)
            # Apply evaluators
            exact = trajectory_exact_match_evaluator(output, row)
            precision = trajectory_precision_evaluator(output, row)
            tool_match = tool_name_match_evaluator(output, row)

            results.append({
                "query": row.get("query"),
                "response": json.loads(output)["agent_response"],
                "tool_calls": json.loads(output)["tool_calls"],
                "exact_match_score": exact.score,
                "precision_score": precision.score,
                "tool_name_match_score": tool_match.score,
                "exact_match_label": exact.label,
                "precision_label": precision.label,
                "tool_name_match_label": tool_match.label,
            })

    df = pd.DataFrame(results)
    print(df.head())
    return df


# async def main():
#     dataset = load_test_data()
#     row  = dataset[0]
#     result = await task_function(row)
#     print("Row:", row)
#     exact = trajectory_exact_match_evaluator(result, row)
#     #result = await call_rag_agent("What is the capital of France?")
#     print("Agent output:")
#     print(result)
#     print("Exact match:", exact)

async def main():
    try:
        df = await run_local_phoenix_experiment()
        print(df)
    finally:
        await close_litellm_async_clients()

if __name__ == "__main__":
    asyncio.run(main())

