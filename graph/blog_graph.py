import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import BlogState
from nodes.research_node import research_node
from nodes.draft_node import draft_node
from nodes.review_node import review_node
from nodes.publish_node import publish_node
from utils.human_review import should_revise


def build_research_graph():
    """
    Graph 1 — runs research → draft → review
    Stops after review. Human reviews in Streamlit.
    """
    graph = StateGraph(BlogState)

    graph.add_node("research", research_node)
    graph.add_node("draft", draft_node)
    graph.add_node("review", review_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "draft")
    graph.add_edge("draft", "review")

    graph.add_conditional_edges(
        "review",
        should_revise,
        {
            "draft": "draft",
            "human_review": END      # stop here for human review
        }
    )

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def build_publish_graph():
    """
    Graph 2 — runs publish only
    Called after human approves.
    """
    graph = StateGraph(BlogState)

    graph.add_node("publish", publish_node)

    graph.set_entry_point("publish")
    graph.add_edge("publish", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def build_revision_graph():
    """
    Graph 3 — runs draft → review only
    Called when human requests revision.
    """
    graph = StateGraph(BlogState)

    graph.add_node("draft", draft_node)
    graph.add_node("review", review_node)

    graph.set_entry_point("draft")
    graph.add_edge("draft", "review")

    graph.add_conditional_edges(
        "review",
        should_revise,
        {
            "draft": "draft",
            "human_review": END
        }
    )

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def get_thread_config(thread_id: str = "blog_session_1") -> dict:
    return {"configurable": {"thread_id": thread_id}}