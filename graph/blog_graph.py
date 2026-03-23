import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import BlogState
from nodes.research_node import research_node
from nodes.draft_node import draft_node
from nodes.review_node import review_node
from nodes.publish_node import publish_node
from utils.human_review import should_revise, should_publish


def build_graph(mode: str = "streamlit"):
    """
    Builds and returns the compiled LangGraph blog writing agent.

    mode: "streamlit" → adds interrupt_before human review node
          "cli"       → no interrupt, human review handled in app.py
    """

    # --- Initialize graph with state schema ---
    graph = StateGraph(BlogState)

    # ─────────────────────────────────────────
    # ADD NODES
    # ─────────────────────────────────────────
    graph.add_node("research", research_node)
    graph.add_node("draft", draft_node)
    graph.add_node("review", review_node)
    graph.add_node("publish", publish_node)

    # Human review node — only needed in streamlit mode
    # In CLI mode, human review is handled manually in app.py
    if mode == "streamlit":
        graph.add_node("human_review", _human_review_placeholder)

    # ─────────────────────────────────────────
    # SET ENTRY POINT
    # ─────────────────────────────────────────
    graph.set_entry_point("research")

    # ─────────────────────────────────────────
    # ADD EDGES
    # ─────────────────────────────────────────

    # research → draft (always)
    graph.add_edge("research", "draft")

    # draft → review (always)
    graph.add_edge("draft", "review")

    # review → conditional:
    #   needs_revision = True  → back to draft
    #   needs_revision = False → human_review (streamlit) or publish (cli)
    if mode == "streamlit":
        graph.add_conditional_edges(
            "review",
            should_revise,
            {
                "draft": "draft",
                "human_review": "human_review"
            }
        )

        # human_review → conditional:
        #   approved    → publish
        #   not approved → draft (revision)
        #   quit        → END
        graph.add_conditional_edges(
            "human_review",
            should_publish,
            {
                "publish": "publish",
                "draft": "draft",
                "end": END
            }
        )

    else:
        # CLI mode — skip human_review node
        # human review handled in app.py loop
        graph.add_conditional_edges(
            "review",
            should_revise,
            {
                "draft": "draft",
                "human_review": "publish"     # goes straight to publish in CLI
            }
        )

    # publish → END (always)
    graph.add_edge("publish", END)

    # ─────────────────────────────────────────
    # COMPILE WITH CHECKPOINTER
    # ─────────────────────────────────────────
    memory = MemorySaver()

    if mode == "streamlit":
        # interrupt_before pauses graph at human_review node
        # Graph state is saved — resumes when user clicks approve/revise
        compiled = graph.compile(
            checkpointer=memory,
            interrupt_before=["human_review"]
        )
    else:
        compiled = graph.compile(
            checkpointer=memory
        )

    return compiled


def _human_review_placeholder(state: dict) -> dict:
    """
    Placeholder node for human review in Streamlit mode.
    Graph pauses BEFORE this node due to interrupt_before.
    Streamlit app updates state directly then resumes.
    """
    return state


def get_thread_config(thread_id: str = "blog_session_1") -> dict:
    """
    Returns the thread config used to resume a paused graph.
    thread_id must be the same across all invoke calls in a session.
    """
    return {"configurable": {"thread_id": thread_id}}