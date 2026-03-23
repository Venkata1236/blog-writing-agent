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
    Reads:  state["blog_draft"]
            state["topic"]
            state["revision_count"]
    Writes: state["review_feedback"]
            state["review_score"]
            state["needs_revision"]
            state["current_node"]
    """
    print("\n🔎 [Review Node] Reviewing blog draft...")

    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.3,          # low temp — consistent evaluation
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

    prompt = f"""
You are a senior blog editor with 10+ years of experience.
Review the following blog post and provide structured feedback.

Topic: {topic}

Blog Draft:
{blog_draft}

Evaluate the blog on these criteria and give a score out of 10 for each:

1. TITLE (Is it compelling and SEO-friendly?)
2. STRUCTURE (Clear intro, sections with headings, conclusion?)
3. CONTENT QUALITY (Accurate, insightful, well-researched?)
4. READABILITY (Engaging tone, clear language, good flow?)
5. PRACTICAL VALUE (Does it give the reader useful takeaways?)

Respond in EXACTLY this format:

TITLE SCORE: [X/10]
STRUCTURE SCORE: [X/10]
CONTENT SCORE: [X/10]
READABILITY SCORE: [X/10]
VALUE SCORE: [X/10]
OVERALL SCORE: [X/10]

STRENGTHS:
[List 2-3 specific things done well]

ISSUES:
[List specific problems that need fixing]

IMPROVEMENT SUGGESTIONS:
[Concrete actionable suggestions]

VERDICT: [APPROVED / NEEDS REVISION]
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    review_text = response.content

    # --- Parse overall score ---
    overall_score = _parse_score(review_text)

    # --- Determine if revision needed ---
    # Auto approve if score >= 7 OR max revisions reached
    max_revisions = 3
    if revision_count >= max_revisions:
        needs_revision = False
        print(f"   Max revisions ({max_revisions}) reached — forcing approval")
    elif overall_score >= 7:
        needs_revision = False
        print(f"   ✅ Score {overall_score}/10 — approved for human review")
    else:
        needs_revision = True
        print(f"   ⚠️  Score {overall_score}/10 — needs revision")

    return {
        **state,
        "review_feedback": review_text,
        "review_score": overall_score,
        "needs_revision": needs_revision,
        "current_node": "review"
    }


def _parse_score(review_text: str) -> int:
    """
    Extracts the overall score from review text.
    Looks for 'OVERALL SCORE: X/10' pattern.
    """
    try:
        lines = review_text.upper().split("\n")
        for line in lines:
            if "OVERALL SCORE" in line:
                # Extract number from "OVERALL SCORE: 8/10"
                parts = line.split(":")
                if len(parts) > 1:
                    score_part = parts[1].strip()
                    score = int(score_part.split("/")[0].strip())
                    return min(max(score, 0), 10)   # clamp between 0-10
    except Exception:
        pass
    return 6    # default score if parsing fails