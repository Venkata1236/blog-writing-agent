# ✍️ Blog Writing Agent

> Multi-node LangGraph agent — Research → Draft → Review → Human Approval → Publish

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-purple)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)
![Tavily](https://img.shields.io/badge/Tavily-Search-blue)

---

## 📌 What Is This?

A multi-node autonomous Blog Writing Agent built with LangGraph. Give it a topic — it researches the web, writes a full blog draft, reviews it for quality, pauses for your approval, and publishes the final polished version. Human-in-the-loop support lets you approve or request revisions before publishing.

---

## 🗺️ Simple Flow
```
User provides topic
        ↓
  [Research Node]
  Tavily searches web → LLM summarizes sources
        ↓
  [Draft Node]
  LLM writes full blog post from research
        ↓
  [Review Node]
  LLM scores quality (Title, Structure, Content, Readability, Value)
  Score < 7 → loops back to Draft Node (max 3 auto-revisions)
        ↓
  [Human Review]
  You read the draft + AI feedback
  Approve → publish | Request changes → Draft Node
        ↓
  [Publish Node]
  Final polish + metadata footer
        ↓
  Download as .md file
```

---

## 🏗️ Detailed Architecture
```
User
 ├── streamlit_app.py   → Web UI (stage-based flow + human review buttons)
 └── app.py             → Terminal interface (menu-driven)
          │
          ▼
      graph/
      ├── state.py          → BlogState TypedDict (shared state across all nodes)
      └── blog_graph.py     → StateGraph — nodes + edges + conditional routing
          │
          ▼
      nodes/
      ├── research_node.py  → Tavily web search + LLM summarization
      ├── draft_node.py     → LLM writes/revises blog draft
      ├── review_node.py    → LLM scores draft quality (0-10)
      └── publish_node.py   → Final polish + metadata footer
          │
          ▼
      utils/
      └── human_review.py   → CLI human review + conditional edge functions
          │
          ▼
      OpenAI API → gpt-4o-mini
      Tavily API → web search
```

---

## 📁 Project Structure
```
blog-writing-agent/
├── app.py                      ← Terminal version (CLI)
├── streamlit_app.py            ← Web UI (deploy this)
├── graph/
│   ├── __init__.py
│   ├── state.py                ← BlogState TypedDict definition
│   └── blog_graph.py          ← StateGraph + nodes + edges + checkpointer
├── nodes/
│   ├── __init__.py
│   ├── research_node.py        ← Node 1 — Tavily search + summarize
│   ├── draft_node.py           ← Node 2 — Write/revise blog
│   ├── review_node.py          ← Node 3 — Score quality
│   └── publish_node.py         ← Node 4 — Final polish
├── utils/
│   ├── __init__.py
│   └── human_review.py         ← Human-in-the-loop + conditional edges
├── .env                        ← API keys (never push!)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 Key Concepts

| Concept | What It Does |
|---|---|
| **StateGraph** | Defines the entire workflow as a directed graph |
| **BlogState** | TypedDict shared across all nodes — single source of truth |
| **Nodes** | Python functions that read + write to state |
| **Conditional Edges** | Route to different nodes based on state values |
| **Human-in-the-Loop** | Graph pauses at human_review node, waits for approval |
| **interrupt_before** | LangGraph feature that pauses graph before a node |
| **MemorySaver** | Checkpointer that saves graph state so it can resume |
| **Revision Loop** | review_score < 7 → loops back to draft_node (max 3 times) |

---

## 🔄 Graph Routing Logic
```python
# After Review Node
needs_revision = True  (score < 7)  → back to Draft Node
needs_revision = False (score >= 7) → Human Review

# After Human Review
human_approved = True  → Publish Node → END
human_feedback exists  → back to Draft Node
user quit              → END
```

---

## ⚙️ Local Setup

**Step 1 — Clone the repo:**
```bash
git clone https://github.com/venkata1236/blog-writing-agent.git
cd blog-writing-agent
```

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Add API keys:**

Create `.env` file:
```
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
```

Create `.streamlit/secrets.toml` for Streamlit:
```toml
OPENAI_API_KEY = "sk-your-openai-key-here"
TAVILY_API_KEY = "tvly-your-tavily-key-here"
```

Get Tavily key free at [tavily.com](https://tavily.com)

**Step 4 — Run:**

Streamlit UI:
```bash
python -m streamlit run streamlit_app.py
```

Terminal version:
```bash
python app.py
```

---

## 💬 Topics To Try
```
The Rise of AI Agents in 2025
How LangGraph is Changing the Way We Build AI Apps
Vector Databases Explained — FAISS vs ChromaDB vs Pinecone
The Future of Electric Vehicles
What is Retrieval-Augmented Generation and Why Does It Matter?
```

---

## 🚀 Deploy on Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → select `streamlit_app.py`
4. Go to Settings → Secrets → add:
```toml
OPENAI_API_KEY = "sk-your-key-here"
TAVILY_API_KEY = "tvly-your-key-here"
```
5. Click Deploy ✅

---

## 📦 Tech Stack

- **LangGraph** — StateGraph, nodes, edges, conditional routing, interrupt_before, MemorySaver
- **LangChain** — ChatOpenAI, HumanMessage
- **OpenAI** — GPT-4o-mini for drafting, reviewing, publishing
- **Tavily** — Web search API for research node
- **Streamlit** — Stage-based web UI with human review buttons
- **python-dotenv** — API key management

---

## 👤 Author

**Venkata Reddy Bommavaram**
- 📧 bommavaramvenkat2003@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/venkatareddy1203)
- 🐙 [GitHub](https://github.com/venkata1236)