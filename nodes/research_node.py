import os
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


def get_api_keys():
    """
    Works both locally (.env) and on Streamlit Cloud (st.secrets)
    """
    try:
        import streamlit as st
        return (
            st.secrets["OPENAI_API_KEY"],
            st.secrets["TAVILY_API_KEY"]
        )
    except Exception:
        return (
            os.getenv("OPENAI_API_KEY"),
            os.getenv("TAVILY_API_KEY")
        )


def research_node(state: dict) -> dict:
    """
    Node 1 — Research the blog topic using Tavily web search.
    Reads:  state["topic"]
    Writes: state["research_summary"]
            state["current_node"]
            state["error"]
    """
    print("\n🔍 [Research Node] Starting research...")

    openai_key, tavily_key = get_api_keys()

    topic = state.get("topic", "")

    if not topic:
        return {
            **state,
            "error": "No topic provided.",
            "current_node": "research"
        }

    try:
        # --- Step 1: Search web with Tavily ---
        print(f"   Searching web for: {topic}")
        tavily = TavilyClient(api_key=tavily_key)

        search_results = tavily.search(
            query=topic,
            search_depth="advanced",      # deeper search
            max_results=5,                # top 5 sources
            include_answer=True           # Tavily's own summary
        )

        # --- Step 2: Extract raw content from results ---
        raw_content = ""

        # Tavily's own answer summary
        if search_results.get("answer"):
            raw_content += f"Overview: {search_results['answer']}\n\n"

        # Individual search results
        for i, result in enumerate(search_results.get("results", []), 1):
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")
            raw_content += f"Source {i}: {title}\n{content}\nURL: {url}\n\n"

        # --- Step 3: Summarize with LLM ---
        print("   Summarizing research with LLM...")
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=openai_key
        )

        summary_prompt = f"""
You are a research assistant. Based on the following web search results about "{topic}", 
create a comprehensive research summary that will be used to write a blog post.

Include:
- Key facts and statistics
- Main concepts and ideas
- Recent developments or trends
- Interesting angles or perspectives
- Any controversies or debates

Keep the summary focused, factual and well-organized.
Aim for 400-500 words.

Raw search results:
{raw_content}

Research Summary:
"""

        response = llm.invoke([HumanMessage(content=summary_prompt)])
        research_summary = response.content

        print("   ✅ Research complete!")

        return {
            **state,
            "research_summary": research_summary,
            "current_node": "research",
            "error": None
        }

    except Exception as e:
        error_msg = f"Research failed: {str(e)}"
        print(f"   ❌ {error_msg}")
        return {
            **state,
            "research_summary": f"Research unavailable. Writing from general knowledge about: {topic}",
            "current_node": "research",
            "error": error_msg
        }