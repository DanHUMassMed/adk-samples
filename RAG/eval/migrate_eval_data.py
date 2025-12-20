from google.adk.evaluation.agent_evaluator import AgentEvaluator
from pathlib import Path

old_path = Path("eval/data/conversation.test.1.json")
new_path = Path("eval/data/conversation.test.1.evalset.json")

AgentEvaluator.migrate_eval_data_to_new_schema(
    old_eval_data_file=str(old_path),
    new_eval_data_file=str(new_path)
)



print(f"✅ Migrated eval data written to {new_path}")
