import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


def get_api_key():
    try:
        import streamlit as st
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def draft_node(state: dict) -> dict:
    """
    Node 2 — Writes the full blog draft using research summary.
    Reads:  state["topic"]
            state["research_summary"]
            state["human_feedback"]     ← on revision turns
            state["blog_draft"]         ← on revision turns
            state["revision_count"]
    Writes: state["blog_draft"]
            state["revision_count"]
            state["current_node"]
    """
    print("\n✍️  [Draft Node] Writing blog draft...")

    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=get_api_key()
    )

    topic = state.get("topic", "")
    research_summary = state.get("research_summary", "")
    human_feedback = state.get("human_feedback", "")
    previous_draft = state.get("blog_draft", "")
    revision_count = state.get("revision_count", 0)

    # --- Build prompt based on whether this is a revision or first draft ---
    if revision_count > 0 and previous_draft and human_feedback:
        print(f"   Revision #{revision_count} — incorporating feedback...")
        prompt = f"""
You are an expert blog writer. You previously wrote a blog draft that needs improvement.

Topic: {topic}

Research Summary:
{research_summary}

Previous Draft:
{previous_draft}

Human Feedback / Revision Request:
{human_feedback}

Please rewrite the blog post incorporating the feedback above.
Keep what was good, fix what was requested.

Blog Post Requirements:
- Title: Compelling, SEO-friendly
- Length: 600-800 words
- Structure: Introduction, 3-4 main sections with subheadings, Conclusion
- Tone: Engaging, informative, conversational
- Include: Key facts from research, practical insights, clear takeaways
- Format: Use markdown formatting (## for headings, **bold** for key terms)

Write the complete revised blog post now:
"""
    else:
        print("   Writing first draft...")
        prompt = f"""
You are an expert blog writer. Write a high-quality, engaging blog post.

Topic: {topic}

Research Summary:
{research_summary}

Blog Post Requirements:
- Title: Compelling, SEO-friendly (start with # Title)
- Length: 600-800 words
- Structure: Introduction, 3-4 main sections with subheadings, Conclusion
- Tone: Engaging, informative, conversational
- Include: Key facts from research, practical insights, clear takeaways
- Format: Use markdown formatting (## for headings, **bold** for key terms)

Write the complete blog post now:
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    blog_draft = response.content

    print("   ✅ Draft complete!")

    return {
        **state,
        "blog_draft": blog_draft,
        "revision_count": revision_count + 1,
        "current_node": "draft",
        "human_feedback": None        # clear feedback after using it
    }
