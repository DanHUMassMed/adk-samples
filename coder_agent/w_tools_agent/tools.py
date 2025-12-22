from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# 1. Define a custom "Code Runner" tool
def local_python_executor(code: str) -> str:
    """
    Executes Python code and returns the printed output. 
    Use this for math, data analysis, or logic.
    """
    try:
        # NOTE: Using exec() is powerful but dangerous. 
        # In production, use a sandbox like 'e2b' or a Docker container.
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            exec(code)
        return f.getvalue()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    code="print(1000 + 111)"
    print("✅ Running code: " + code)
    ret_val = local_python_executor(code)
    print("✅ Result: " + ret_val)