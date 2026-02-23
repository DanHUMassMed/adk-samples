import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from academic_research.acedemic_research_local.agent import root_agent

async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="test_app")
    
    await runner.session_service.create_session(app_name="test_app", user_id="user1", session_id="session1")
    
    with open("academic_research/data/1706.03762v7.pdf", "rb") as f:
        pdf_bytes = f.read()
        
    part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
    content = types.Content(role='user', parts=[part, types.Part.from_text(text="What are the main research directions of this paper and who cited it recently?")])
    
    events = runner.run_async(user_id="user1", session_id="session1", new_message=content)
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                print("\nFINAL RESPONSE:\n", event.content.parts[0].text)
        elif event.is_error():
            print("\nERROR:\n", event.error_details)
        elif event.content and event.content.parts:
            # We can print intermediate steps if we want
            pass

if __name__ == '__main__':
    asyncio.run(main())
