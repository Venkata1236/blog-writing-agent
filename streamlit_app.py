import streamlit as st
import os
from dotenv import load_dotenv
from graph.blog_graph import build_graph, get_thread_config
from graph.state import BlogState

load_dotenv()


# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Blog Writing Agent",
    page_icon="✍️",
    layout="centered"
)


# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
def initialize_session():
    if "graph" not in st.session_state:
        st.session_state.graph = None
    if "thread_config" not in st.session_state:
        st.session_state.thread_config = None
    if "current_state" not in st.session_state:
        st.session_state.current_state = None
    if "stage" not in st.session_state:
        st.session_state.stage = "input"
    if "topic" not in st.session_state:
        st.session_state.topic = ""
    if "final_blog" not in st.session_state:
        st.session_state.final_blog = None


def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


initialize_session()


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.title("✍️ Blog Writing Agent")
    st.markdown("---")

    st.markdown("### 🔄 Pipeline Stages")
    stages = {
        "input":        "📝 Topic Input",
        "researching":  "🔍 Researching",
        "drafting":     "✍️ Drafting",
        "reviewing":    "🔎 Reviewing",
        "human_review": "👤 Your Review",
        "publishing":   "📢 Publishing",
        "done":         "✅ Done"
    }
    current = st.session_state.stage
    for key, label in stages.items():
        if key == current:
            st.markdown(f"**→ {label}**")
        else:
            st.markdown(f"　　{label}")

    st.markdown("---")

    if st.button("🔄 Start Over", use_container_width=True):
        reset_session()
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        "Multi-node LangGraph agent that researches, "
        "drafts, reviews, and publishes blog posts. "
        "Human-in-the-loop approval before publishing."
    )


# ─────────────────────────────────────────
# HELPER — RUN GRAPH UNTIL INTERRUPT
# ─────────────────────────────────────────
def run_until_interrupt(initial_state=None, resume_state=None):
    graph = st.session_state.graph
    config = st.session_state.thread_config
    input_state = initial_state if initial_state else resume_state

    try:
        # Use invoke instead of stream
        result = graph.invoke(input_state, config=config)
        return result
    except Exception as e:
        st.error(f"❌ Agent error: {str(e)}")
        return None


# ─────────────────────────────────────────
# STAGE 1 — TOPIC INPUT
# ─────────────────────────────────────────
if st.session_state.stage == "input":

    st.title("✍️ Blog Writing Agent")
    st.markdown(
        "Powered by **LangGraph** — Research → Draft → Review "
        "→ Human Approval → Publish"
    )
    st.markdown("---")

    st.subheader("📝 What would you like to write about?")

    topic = st.text_input(
        "Blog Topic",
        placeholder="e.g. The Future of AI in Healthcare"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start = st.button(
            "🚀 Start Writing Agent",
            use_container_width=True,
            disabled=not topic.strip()
        )

    if start and topic.strip():
        st.session_state.topic = topic.strip()
        st.session_state.stage = "researching"

        # Build graph
        st.session_state.graph = build_graph(mode="streamlit")
        st.session_state.thread_config = get_thread_config("streamlit_session_1")

        st.rerun()


# ─────────────────────────────────────────
# STAGE 2 — RUNNING AGENT (research → draft → review)
# ─────────────────────────────────────────
elif st.session_state.stage in ["researching", "drafting", "reviewing"]:

    st.title("✍️ Blog Writing Agent")
    st.markdown(f"**Topic:** {st.session_state.topic}")
    st.markdown("---")

    st.info("⏳ Agent is working through all stages — this may take 30-60 seconds...")

    with st.spinner("🔍 Researching → ✍️ Drafting → 🔎 Reviewing..."):
        initial_state: BlogState = {
            "topic": st.session_state.topic,
            "research_summary": None,
            "blog_draft": None,
            "review_feedback": None,
            "review_score": None,
            "needs_revision": None,
            "human_approved": None,
            "human_feedback": None,
            "final_blog": None,
            "revision_count": 0,
            "current_node": None,
            "error": None
        }

        try:
            graph = st.session_state.graph
            config = st.session_state.thread_config
            final_state = None

            final_state = run_until_interrupt(initial_state=initial_state)

            if final_state:
                st.session_state.current_state = final_state
                # Check if needs human review or already published
                if final_state.get("final_blog"):
                    st.session_state.stage = "done"
                    st.session_state.final_blog = final_state.get("final_blog")
                else:
                    st.session_state.stage = "human_review"
                st.rerun()
            else:
                st.error("❌ Agent failed to produce output. Please try again.")

        except Exception as e:
            st.error(f"❌ Agent error: {str(e)}")


# ─────────────────────────────────────────
# STAGE 3 — HUMAN REVIEW
# ─────────────────────────────────────────
elif st.session_state.stage == "human_review":

    st.title("👤 Your Review")
    st.markdown(f"**Topic:** {st.session_state.topic}")
    st.markdown("---")

    state = st.session_state.current_state

    # --- Show AI review score ---
    review_score = state.get("review_score", 0)
    revision_count = state.get("revision_count", 0)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("AI Review Score", f"{review_score}/10")
    with col2:
        st.metric("Revisions So Far", revision_count)

    st.markdown("---")

    # --- Show blog draft ---
    st.subheader("📝 Blog Draft")
    blog_draft = state.get("blog_draft", "")
    st.markdown(blog_draft)

    st.markdown("---")

    # --- Show AI feedback ---
    with st.expander("🔎 View AI Review Feedback"):
        st.markdown(state.get("review_feedback", "No feedback available."))

    st.markdown("---")

    # --- Human decision ---
    st.subheader("What would you like to do?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "✅ Approve & Publish",
            use_container_width=True
        ):
            updated_state = {
                **state,
                "human_approved": True,
                "human_feedback": None
            }
            st.session_state.current_state = updated_state
            st.session_state.stage = "publishing"
            st.rerun()

    with col2:
        if st.button(
            "🔄 Request Revision",
            use_container_width=True
        ):
            st.session_state.stage = "revision_input"
            st.rerun()


# ─────────────────────────────────────────
# STAGE 4 — REVISION INPUT
# ─────────────────────────────────────────
elif st.session_state.stage == "revision_input":

    st.title("🔄 Request Revision")
    st.markdown(f"**Topic:** {st.session_state.topic}")
    st.markdown("---")

    st.subheader("💬 What changes would you like?")
    st.caption("Be specific — the agent will rewrite based on your feedback.")

    feedback = st.text_area(
        "Your Feedback",
        placeholder=(
            "e.g. Make the intro more engaging, "
            "add more statistics, shorten section 2..."
        ),
        height=150
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit = st.button(
            "🚀 Send for Revision",
            use_container_width=True,
            disabled=not feedback.strip()
        )

    if submit and feedback.strip():
        updated_state = {
            **st.session_state.current_state,
            "human_approved": False,
            "human_feedback": feedback.strip(),
            "needs_revision": True
        }
        st.session_state.current_state = updated_state
        st.session_state.stage = "drafting"

        with st.spinner("🔄 Revising your blog..."):
            final_state = run_until_interrupt(
                resume_state=updated_state
            )

        if final_state:
            st.session_state.current_state = final_state
            st.session_state.stage = "human_review"
            st.rerun()


# ─────────────────────────────────────────
# STAGE 5 — PUBLISHING
# ─────────────────────────────────────────
elif st.session_state.stage == "publishing":

    st.title("📢 Publishing...")
    st.markdown(f"**Topic:** {st.session_state.topic}")
    st.markdown("---")

    with st.spinner("📢 Preparing your final blog post..."):
        final_state = run_until_interrupt(
            resume_state=st.session_state.current_state
        )

    if final_state:
        st.session_state.current_state = final_state
        st.session_state.final_blog = final_state.get("final_blog", "")
        st.session_state.stage = "done"
        st.rerun()


# ─────────────────────────────────────────
# STAGE 6 — DONE
# ─────────────────────────────────────────
elif st.session_state.stage == "done":

    st.title("🎉 Blog Published!")
    st.markdown(f"**Topic:** {st.session_state.topic}")
    st.markdown("---")

    st.balloons()

    state = st.session_state.current_state
    final_blog = (
        st.session_state.final_blog or
        state.get("final_blog", "") or
        state.get("blog_draft", "")      # fallback to draft if final not generated
    )

    # --- Stats ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("AI Review Score", f"{state.get('review_score', 0)}/10")
    with col2:
        st.metric("Revisions", state.get("revision_count", 0))
    with col3:
        word_count = len(final_blog.split()) if final_blog else 0
        st.metric("Word Count", f"~{word_count}")

    st.markdown("---")

    # --- Final blog ---
    st.subheader("📝 Your Published Blog Post")
    if final_blog:
        st.markdown(final_blog)
    else:
        st.warning("Blog content could not be loaded. Please try again.")

    st.markdown("---")

    # --- Download button ---
    st.download_button(
        label="⬇️ Download Blog as Markdown",
        data=final_blog,
        file_name=f"{st.session_state.topic.replace(' ', '_').lower()}_blog.md",
        mime="text/markdown",
        use_container_width=True
    )