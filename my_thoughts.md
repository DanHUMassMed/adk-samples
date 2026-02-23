# My Thoughts on the LiteLLM/PDF Issue

## What I Have Done So Far
1. **Reviewed the Environment and Code**: I looked at how `agent.py` is configuring the `LiteLlm` wrapper with `openai/gpt-oss:20b` pointing to a local endpoint (`http://localhost:11434/v1`).
2. **Consulted the Documentation**: I searched through the `llms-full.txt` documentation and ADK's `lite_llm.py` source code inside your `.venv` to understand how the library handles PDF attachments (`application/pdf`).
3. **Identified the Formatting Bug**: I found that when the ADK's `lite_llm.py` sees `openai/` as the provider in the model string, it assumes it is talking to the real OpenAI backend. Thus, it tries to use the OpenAI Assistants `file_id` upload feature (`litellm.acreate_file`) to upload the PDF. 
4. **Tested Workarounds**: I ran tests using different provider prefixes (like `custom_openai/` or `ollama_chat/`). While that stops ADK from trying to call the missing `/v1/files` upload endpoint, it then attempts to pass the PDF's raw base64 bytes directly into the content array. Local models generally cannot parse binary PDF data fed directly into the completion prompt.

## Why This is a Hard Problem
This is a challenging problem because it lies at the intersection of three different layers of abstraction, making assumptions about each other:
1. **The LLM (Ollama)**: Local models run via Ollama are typically text-in/text-out (or vision). They do not have built-in OCR or PDF parsing engines running natively behind their API.
2. **The Router (LiteLLM)**: LiteLLM translates API formats, but it does not inherently parse documents. It either passes raw bytes or uploads files to endpoints that explicitly support file IDs.
3. **The Framework (ADK)**: The ADK attempts to abstract multimodal inputs. Since OpenAI natively supports uploading PDFs to their backend to be parsed, ADK assumes any `openai/` model can do the same. When applied to a local mock-OpenAI endpoint, this abstraction leaks and breaks because the local server lacks a document parsing backend.

Attempting to fix this simply by changing strings in the ADK configuration will not work, because ultimately, the local LLM needs raw text, not a base64 encoded PDF binary stream.

## What Might Work (Moving Forward)

To solve this, we cannot rely on the LLM or LiteLLM to magically parse the PDF binary for us. We must extract the text *before* the LLM sees it. Here are the most viable paths forward:

1. **Pre-processing the Input**:
   Instead of handing the agent a raw PDF file object, we can use the `pypdf` library (which I noticed is already installed in your `pyproject.toml`) to extract the text from `1706.03762v7.pdf`. We would then pass the *extracted text string* as the input to the agent. This is the most bulletproof solution, as the LLM will just be reading a massive text block.

2. **Middleware/Interceptors**:
   We can intercept the request before it hits the `LiteLlm` client inside ADK and convert any `application/pdf` parts into plain `text` parts by parsing the bytes in memory. 

3. **Creating a "ReadPDF" Tool**:
   Rather than stuffing the entire PDF into the context window up front, we could pass the file path to the agent and give it a tool (e.g., `read_pdf_tool`) using `pypdf`. The agent would call this tool to fetch pieces of the paper as needed. This approach uses tokens much more efficiently.

### Implementation Details & Trade-offs

#### 1. Pre-processing the Input
**Implementation:**
We modify the script that calls `adk run` (or the code invoking the agent) to first open the PDF using `pypdf.PdfReader`, loop through the pages, and extract the text into a single string. We then pass this string to the agent instead of the PDF file path.
**Trade-offs:**
- *Pros:* Easiest to implement. Extremely robust because the LLM only sees plain text, avoiding any framework/formatting bugs.
- *Cons:* Balloons the context window. Extremely long PDFs will consume masive amounts of tokens, slowing down inference drastically or hitting the model's token limit.
- *Success Likelihood:* **High**. This is virtually guaranteed to work because it relies entirely on standard text generation.

#### 2. Middleware/Interceptors (Before-Request Hook)
**Implementation (Refined Plan):**
We create a custom agent `before_request` hook interceptor for the ADK. Before the request is sent to the local endpoint, the interceptor scans the `LlmRequest` payload for any attached `application/pdf` files.
1. When it finds a PDF, it opens the file using `pypdf`, extracts all the text, and saves it to a new plain `.txt` file on disk.
2. It then mutates the `LlmRequest` object in-flight, stripping out the `application/pdf` multimodal part.
3. It replaces that part with a system or user prompt instructing the LLM to read the newly generated plain `.txt` file (for example, by either mounting the `.txt` file natively or pulling the extracted text directly into the prompt payload).

**Trade-offs:**
- *Pros:* Cleanest experience for the end user calling the agent. The user can simply pass a PDF file, and the framework handles things transparently behind the scenes without needing script-level changes.
- *Cons:* We must dive into ADK internals to write the `before_request` hook correctly and mutate the `LlmRequest` object in-flight. 
- *Success Likelihood:* **High** (Upgraded from Medium-High). By shifting the strategy so the hook simply pre-processes the file into raw text and swaps the payload, we bypass all of the ADK/LiteLLM binary parsing edge cases. As long as the hook successfully mutates the ADK `LlmRequest.contents` arrays before the LiteLlm adapter kicks in, the LLM will just be processing standard text, ensuring a very high likelihood of success.

#### 3. Creating a "ReadPDF" Tool
**Implementation:**
We build a custom ADK `Tool` (e.g. `read_pdf_tool`) that takes a file path and an optional page range or search query. It uses `pypdf` behind the scenes to fetch specific chunks of the document. We then pass this tool to the `academic_coordinator` and provide the PDF's file path in the prompt instead of as a multimodal attachment.
**Trade-offs:**
- *Pros:* Extremely token-efficient. The model only reads the parts of the paper it needs, which is ideal for massive academic papers. It scales beautifully.
- *Cons:* Hardest to implement correctly. The agent has to understand how to iterate through the document using the tool. A smaller/weaker local model (like a 20b parameter model) might get stuck in loops, fail to find the right information, or struggle to use the tool effectively.
- *Success Likelihood:* **Medium**. While architecturally the best, its success depends heavily on the reasoning capabilities of the `gpt-oss:20b` model to use the tool correctly.

### My Recommendation
The most likely to succeed immediately is **Option 1 (Pre-processing the Input)**, as it completely side-steps the framework's file-handling logic and relies on the LLM's core strength: reading text. If token limits become an issue, we should pivot to **Option 3 (Creating a ReadPDF Tool)**.

Let me know if you would like me to implement one of these paths!
