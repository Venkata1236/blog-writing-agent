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


def review_node(state: dict) -> dict:
    """
    Node 3 — Reviews the blog draft for quality.
    Makes TWO separate LLM calls:
    1. Get detailed feedback (text)
    2. Get score (number only — no parsing needed)
    """
    print("\n🔎 [Review Node] Reviewing blog draft...")

    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=get_api_key()
    )

    topic = state.get("topic", "")
    blog_draft = state.get("blog_draft", "")
    revision_count = state.get("revision_count", 0)

    if not blog_draft:
        return {
            **state,
            "review_feedback": "No draft to review.",
            "review_score": 0,
            "needs_revision": True,
            "current_node": "review"
        }

    # --- Call 1: Get detailed feedback ---
    feedback_prompt = f"""
You are a senior blog editor. Review this blog post about "{topic}".

Blog Draft:
{blog_draft}

Provide structured feedback:

STRENGTHS:
[List 2-3 specific things done well]

ISSUES:
[List specific problems]

IMPROVEMENT SUGGESTIONS:
[Concrete actionable suggestions]

VERDICT: [APPROVED / NEEDS REVISION]
"""

    feedback_response = llm.invoke([HumanMessage(content=feedback_prompt)])
    review_feedback = feedback_response.content

    # --- Call 2: Get score as a number ONLY ---
    score_prompt = f"""
You are a blog editor. Rate this blog post about "{topic}" on a scale of 1 to 10.

Blog Draft:
{blog_draft}

Respond with ONLY a single integer number between 1 and 10.
No explanation. No text. Just the number.
Example: 8
"""

    score_response = llm.invoke([HumanMessage(content=score_prompt)])
    score_text = score_response.content.strip()

    # Parse score — should be just a number now
    try:
        overall_score = int(score_text.split()[0])
        overall_score = min(max(overall_score, 0), 10)
    except Exception:
        print(f"   ⚠️ Score parsing failed on '{score_text}' — defaulting to 7")
        overall_score = 7

    print(f"   📊 Score: {overall_score}/10")

    # --- Decide if revision needed ---
    max_revisions = 3
    if revision_count >= max_revisions:
        needs_revision = False
        print(f"   Max revisions reached — forcing human review")
    elif overall_score >= 7:
        needs_revision = False
        print(f"   ✅ Score {overall_score}/10 — sending to human review")
    else:
        needs_revision = True
        print(f"   ⚠️  Score {overall_score}/10 — needs revision")

    return {
        **state,
        "review_feedback": review_feedback,
        "review_score": overall_score,
        "needs_revision": needs_revision,
        "current_node": "review"
    }