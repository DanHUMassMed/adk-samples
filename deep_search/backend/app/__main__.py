import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# Define the directory where your ADK agents are located
AGENTS_DIR = "."

# Get the FastAPI application instance
app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=False,  # Set to True if you want the developer UI
    host="127.0.0.1",
    port=8000,
    # You can specify other service URIs if needed, for example:
    # session_service_uri="sqlite:///./.adk/sessions.db",
    # artifact_service_uri="file:///./.adk/artifacts",
    # memory_service_uri="in_memory",
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

