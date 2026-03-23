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


def publish_node(state: dict) -> dict:
    """
    Node 4 — Polishes and formats the final blog post for publishing.
    Reads:  state["blog_draft"]
            state["topic"]
            state["review_feedback"]
            state["revision_count"]
    Writes: state["final_blog"]
            state["current_node"]
    """
    print("\n📢 [Publish Node] Preparing final blog post...")

    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=get_api_key()
    )

    topic = state.get("topic", "")
    blog_draft = state.get("blog_draft", "")
    review_feedback = state.get("review_feedback", "")
    revision_count = state.get("revision_count", 0)

    if not blog_draft:
        return {
            **state,
            "final_blog": "No blog draft available to publish.",
            "current_node": "publish"
        }

    prompt = f"""
You are a professional blog editor preparing a final post for publishing.

Topic: {topic}

Blog Draft:
{blog_draft}

Review Feedback (for reference):
{review_feedback}

Your job is to do a final polish:
1. Fix any grammar or spelling issues
2. Ensure the title is compelling and on a single line starting with #
3. Make sure all section headings use ## 
4. Ensure the introduction hooks the reader in the first 2 sentences
5. Make sure the conclusion ends with a clear call to action
6. Add a metadata section at the very end in this exact format:

---
📊 Blog Stats:
- Word Count: [approximate word count]
- Reading Time: [X min read]
- Revisions: {revision_count}
- Topic: {topic}
---

Return the complete polished blog post ready to publish.
Do not add any commentary — just the final blog post.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    final_blog = response.content

    print("   ✅ Blog post ready to publish!")

    return {
        **state,
        "final_blog": final_blog,
        "current_node": "publish"
    }
