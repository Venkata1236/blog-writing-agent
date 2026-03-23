from typing import TypedDict, Optional


class BlogState(TypedDict):
    """
    Shared state that flows between all nodes in the graph.
    Every node reads from and writes to this state.
    """

    # --- Input ---
    topic: str                          # Blog topic provided by user

    # --- Research Node output ---
    research_summary: Optional[str]     # Summarized research from Tavily

    # --- Draft Node output ---
    blog_draft: Optional[str]           # Full blog draft written by LLM

    # --- Review Node output ---
    review_feedback: Optional[str]      # Reviewer's feedback on the draft
    review_score: Optional[int]         # Quality score out of 10
    needs_revision: Optional[bool]      # True if draft needs rewriting

    # --- Human-in-the-loop ---
    human_approved: Optional[bool]      # True if human approved the draft
    human_feedback: Optional[str]       # Human's revision notes (if any)

    # --- Publish Node output ---
    final_blog: Optional[str]           # Final polished blog post

    # --- Control ---
    revision_count: Optional[int]       # How many times draft was revised
    current_node: Optional[str]         # Tracks which node is running
    error: Optional[str]                # Stores any error messages