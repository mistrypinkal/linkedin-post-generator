# 🤖 LinkedIn Post Generator — Agentic AI

An agentic AI system that automatically generates high-quality LinkedIn posts for AI niches (Generative AI, Agentic AI, RAG, Multimodal RAG) using a multi-step LangGraph pipeline.

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                  LangGraph Pipeline                     │
│                                                         │
│  [Research] → [Hooks] → [Draft] → [Quality Check]      │
│                                         │               │
│                              ┌──────────┴────────┐      │
│                              ▼                   ▼      │
│                          [Refine]          [Hashtags]   │
│                              └──────────────────┘       │
└─────────────────────────────────────────────────────────┘
    │
    ▼
Streamlit UI (with LangSmith Tracing)
```

### Pipeline Nodes

| Node | Model | Role |
|------|-------|------|
| **Research** | GPT-4o-mini | Extracts 5 key insights about the topic |
| **Hook Generation** | GPT-4o-mini | Creates 3 scroll-stopping hook alternatives |
| **Draft Post** | GPT-4o | Writes the full LinkedIn post in required format |
| **Quality Check** | Logic | Checks word count, format, refinement needs |
| **Refinement** | GPT-4o | Polishes post if over 220 words or feedback given |
| **Hashtag Engine** | GPT-4o-mini | Generates 8-10 strategic LinkedIn hashtags |

---

## 🚀 Setup & Installation

### 1. Clone / Extract the project
```bash
cd linkedin-post-generator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
```bash
cp .env.example .env
# Edit .env with your keys
```

Required:
- `OPENAI_API_KEY` — from [platform.openai.com](https://platform.openai.com)

Optional (for tracing):
- `LANGCHAIN_API_KEY` — from [smith.langchain.com](https://smith.langchain.com)
- `LANGCHAIN_PROJECT` — project name for LangSmith

### 4. Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
linkedin-post-generator/
├── app.py                    # Streamlit frontend
├── requirements.txt
├── .env.example
├── graphs/
│   └── post_graph.py         # LangGraph state machine
├── prompts/
│   └── templates.py          # All LangChain prompt templates
├── utils/
│   ├── helpers.py            # Word count, section parsing
│   └── tracing.py            # LangSmith setup
└── agents/
    └── __init__.py
```

---

## 📝 Post Format

Every generated post follows this structure:

1. **Hook** (1 line) — Bold, scroll-stopping statement
2. **Description** (2 lines) — Concise story or explanation  
3. **Key Highlights** (max 5 bullets) — Impactful, jargon-free insights
4. **Closing Statement** (1 line) — Motivational call to engage
5. **Hashtags** — 8-10 strategic LinkedIn hashtags

Strict limit: **under 220 words**

---

## 🔍 LangSmith Tracing

When configured, every pipeline run is traced in LangSmith showing:
- Node-by-node execution
- Token usage per step
- Latency breakdown
- Input/output for each LLM call

---

## 🎯 Supported Niches

- **Generative AI** — LLMs, foundation models, prompt engineering
- **Agentic AI** — Autonomous agents, multi-agent systems, tool-calling
- **RAG** — Retrieval-Augmented Generation, vector search, embeddings
- **Multimodal RAG** — Vision-language models, document AI, image retrieval
