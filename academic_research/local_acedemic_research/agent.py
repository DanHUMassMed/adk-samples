
import io
import litellm
from pypdf import PdfReader
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from . import prompt
from .sub_agents.academic_newresearch import academic_newresearch_agent
from .sub_agents.academic_websearch import academic_websearch_agent

litellm._turn_on_debug()

MODEL=LiteLlm(model="openai/gpt-oss:20b",
            api_base="http://localhost:11434/v1", 
            api_key="my_api_key")

def intercept_and_parse_pdf(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Intercepts requests with PDFs and converts them to raw text."""
    
    # # ✅ Write full LlmRequest to file for DEBUGGING
    # try:
    #     serialized = repr(llm_request)
    #     with open("LlmRequest.txt", "w") as f:
    #         if isinstance(serialized, dict):
    #             json.dump(serialized, f, indent=2)
    #         else:
    #             f.write(str(serialized))
    # except Exception as e:
    #     print(f"Failed to write LlmRequest to file: {e}")


    if not llm_request.contents:
        return None
        
    for content in llm_request.contents:
        if not content.parts:
            continue
            
        new_parts = []
        for part in content.parts:
            # Handle inline PDF data
            if part.inline_data and getattr(part.inline_data, 'mime_type', '') == 'application/pdf':
                try:
                    reader = PdfReader(io.BytesIO(part.inline_data.data))
                    extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                    # Save to text file as requested in plan options
                    with open("parsed_paper.txt", "w") as f:
                        f.write(extracted_text)
                    new_parts.append(types.Part(text=f"The following is the extracted text from the PDF document:\n\n{extracted_text}"))
                except Exception as e:
                    print(f"Failed to parse inline PDF: {e}")
                    new_parts.append(part)
            # Handle referenced PDF file paths
            elif part.file_data and hasattr(part.file_data, 'file_uri') and str(part.file_data.file_uri).endswith('.pdf'):
                try:
                    # Strip gs:// or other schemas if needed, assuming local path for now
                    uri = part.file_data.file_uri
                    if uri.startswith('file://'):
                        uri = uri[7:]
                        
                    reader = PdfReader(uri)
                    extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                    with open("parsed_paper.txt", "w") as f:
                        f.write(extracted_text)
                    new_parts.append(types.Part(text=f"The following is the extracted text from the PDF document '{uri}':\n\n{extracted_text}"))
                except Exception as e:
                    print(f"Failed to parse file URI PDF: {e}")
                    new_parts.append(part)
            else:
                new_parts.append(part)
                
        content.parts = new_parts
        
    return None

academic_coordinator = LlmAgent(
    name="academic_coordinator",
    model=MODEL,
    description=(
        "analyzing seminal papers provided by the users, "
        "providing research advice, locating current papers "
        "relevant to the seminal paper, generating suggestions "
        "for new research directions, and accessing web resources "
        "to acquire knowledge"
    ),
    instruction=prompt.ACADEMIC_COORDINATOR_PROMPT,
    output_key="seminal_paper",
    tools=[
        AgentTool(agent=academic_websearch_agent),
        AgentTool(agent=academic_newresearch_agent),
    ],
    before_model_callback=intercept_and_parse_pdf,
)

root_agent = academic_coordinator
