# Blogger Writer Agent

A sophisticated technical blogging assistant built with the [Google Agent Developer Kit (ADK)](https://github.com/google/adk). This agent uses a multi-agent architecture to collaborate with you to plan, write, edit, and promote high-quality technical blog posts.

## 🚀 Features

*   **Collaborative Workflow:** Guides you through a structured process from planning to export.
*   **Codebase Analysis:** Can analyze a local directory to write accurate, code-aware articles.
*   **Intelligent Planning:** Generates comprehensive outlines using web search (DuckDuckGo) and codebase context.
*   **Multi-Agent Architecture:**
    *   **Planner:** Creates detailed outlines.
    *   **Writer:** Drafts in-depth technical content.
    *   **Editor:** Refines content based on your feedback.
    *   **Social Media:** Generates Twitter and LinkedIn promotion posts.
*   **Visuals & Media:** Supports placeholder strategies for images and video.
*   **Observability:** Integrated tracing with **Arize Phoenix** for debugging and performance monitoring.
*   **Local LLM Support:** configured out-of-the-box to work with local models via **Ollama**.

## 🛠️ Prerequisites

*   **Python 3.13+**
*   **[Ollama](https://ollama.com/)** running locally (default endpoint: `http://localhost:11434/v1`)
*   **[uv](https://github.com/astral-sh/uv)** (recommended for dependency management) or `pip`

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd blogger_writer
    ```

2.  **Install Dependencies:**
    Using `uv` (recommended):
    ```bash
    uv sync
    ```
    Or using `pip`:
    ```bash
    pip install .
    ```

3.  **Setup Ollama:**
    Ensure Ollama is running and pull the model you intend to use. The default configuration expects a model compatible with the configured name.
    ```bash
    ollama pull llama3  # or mistral, etc.
    ```

## ⚙️ Configuration

The agent configuration is located in `blogger_agent/config.py`.

*   **Model:** By default, it connects to `http://localhost:11434/v1`.
*   **`worker_model`**: The model used for generation (planning, writing).
*   **`critic_model`**: The model used for evaluation and editing.

**Note:** You may need to update `blogger_agent/config.py` to match your pulled Ollama model name (e.g., change `"openai/gpt-oss:20b"` to `"llama3"`).

```python
# blogger_agent/config.py
@dataclass
class ResearchConfiguration:
    critic_model: str = "llama3"  # Update this
    worker_model: str = "llama3"  # Update this
    ...
```

## 🏃 Usage

To run the agent, you need a simple entry script. Create a file named `run_agent.py` in the root directory:

```python
# run_agent.py
from blogger_agent.agent import root_agent

if __name__ == "__main__":
    # Start the interactive session
    root_agent.run()
```

Then execute it:

```bash
# If using uv
uv run run_agent.py

# If using standard python
python run_agent.py
```

### Workflow
1.  **Analyze:** Optional. Provide a path to your code to help the agent understand technical details.
2.  **Plan:** The agent proposes an outline. Review and refine it.
3.  **Visuals:** Decide on image placeholders.
4.  **Write:** The agent drafts the full post.
5.  **Edit:** Provide feedback to refine the draft.
6.  **Social Media:** Generate promotion posts.
7.  **Export:** Save the final result to a Markdown file.

## 🔍 Tracing & Debugging

This project uses **Arize Phoenix** for tracing. When you run the agent, it will automatically instrument calls and start a local Phoenix server (usually at `http://localhost:6006`).

Visit the Phoenix UI to visualize agent execution traces, tool calls, and latency.

## 📂 Project Structure

```
blogger_writer/
├── blogger_agent/
│   ├── agent.py            # Main interactive agent definition
│   ├── config.py           # Configuration (models, params)
│   ├── tools.py            # Tools (Search, File I/O, Code Analysis)
│   ├── tracing.py          # Phoenix instrumentation
│   └── sub_agents/         # Specialized agents
│       ├── blog_planner.py
│       ├── blog_writer.py
│       ├── blog_editor.py
│       └── social_media_writer.py
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```
