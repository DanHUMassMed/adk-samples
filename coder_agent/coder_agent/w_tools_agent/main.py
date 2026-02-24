import os

import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session service URI (e.g., SQLite)
# Note: Use 'sqlite+aiosqlite' instead of 'sqlite' because DatabaseSessionService requires an async driver
#SESSION_SERVICE_URI = "sqlite+aiosqlite:///./sessions.db"
SESSION_SERVICE_URI = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('capital_agent') matches your agent folder
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# You can add more FastAPI routes or configurations below if needed
# Example:
# @app.get("/hello")
# async def read_root():
#     return {"Hello": "World"}

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)


# SEE DOCUMENTATION AT https://google.github.io/adk-docs/deploy/cloud-run/#gcloud-cli-for-python

# Test
# curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
# curl -X GET  http://0.0.0.0:8080/list-apps


# curl -X POST http://0.0.0.0:8080/apps/w_tools_agent/users/user_123/sessions/session_abc \
#     -H "Content-Type: application/json" \
#     -d '{"preferred_language": "English", "visit_count": 5}'

# {"id":"session_abc","appName":"w_tools_agent","userId":"user_123","state":{"preferred_language":"English","visit_count":5},
# "events":[],"lastUpdateTime":1766531207.0}


# curl -X POST http://0.0.0.0:8080/run_sse \
#     -H "Content-Type: application/json" \
#     -d '{
#     "app_name": "w_tools_agent",
#     "user_id": "user_123",
#     "session_id": "session_abc",
#     "new_message": {
#         "role": "user",
#         "parts": [{
#         "text": "What is 2 + 2?"
#         }]
#     },
#     "streaming": false
#     }'
# data: {"content":{"parts":[{"text":"The result of 2 + 2 is **4**."}],"role":"model"},"partial":false,
# "usageMetadata":{"candidatesTokenCount":53,"promptTokenCount":325,"totalTokenCount":378},"invocationId":"e-904c5c5e-805b-4b0d-ab80-0e2e1dc3c47b",
# "author":"code_assistant","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"d69074c4-48d4-440b-8abb-4ad84e98d6eb",
# "timestamp":1766531349.168908}