import asyncio
from google.genai import types
from google.adk.models.lite_llm import LiteLlm, _get_content
from google.adk.models.llm_request import LlmRequest

async def main():
    part = types.Part(inline_data=types.Blob(data=b'hello pdf', mime_type='application/pdf'))
    content = await _get_content([part], provider='custom_openai', model='custom_openai/test')
    print("custom_openai output:", content)

    content2 = await _get_content([part], provider='ollama_chat', model='ollama_chat/test')
    print("ollama_chat output:", content2)

if __name__ == '__main__':
    asyncio.run(main())
