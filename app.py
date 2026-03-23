import os
import sys
from dotenv import load_dotenv
from graph.blog_graph import build_graph, get_thread_config
from graph.state import BlogState
from utils.human_review import get_human_review, should_publish

load_dotenv()


def print_separator():
    print("\n" + "=" * 60 + "\n")


def print_welcome():
    print_separator()
    print("✍️  BLOG WRITING AGENT — CLI MODE")
    print("    Powered by LangGraph + OpenAI + Tavily")
    print_separator()
    print("How it works:")
    print("  1. You provide a blog topic")
    print("  2. Agent researches the topic (Tavily)")
    print("  3. Agent writes a draft (GPT-4o-mini)")
    print("  4. Agent reviews for quality (GPT-4o-mini)")
    print("  5. You approve or request changes")
    print("  6. Agent publishes final version")
    print_separator()


def check_api_keys():
    """
    Validates required API keys are present.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not openai_key:
        print("❌ OPENAI_API_KEY not found in .env file.")
        sys.exit(1)

    if not tavily_key:
        print("⚠️  TAVILY_API_KEY not found — research will use fallback mode.")

    print("✅ API keys loaded.\n")


def get_topic():
    """
    Gets blog topic from user.
    """
    print("📝 What would you like to write a blog about?\n")
    topic = input("Blog Topic: ").strip()

    while not topic:
        print("⚠️  Topic cannot be empty.")
        topic = input("Blog Topic: ").strip()

    return topic


def run_cli():
    """
    Main CLI loop — runs the blog writing agent in terminal.
    """
    print_welcome()
    check_api_keys()

    # --- Get topic ---
    topic = get_topic()
    print_separator()

    # --- Build graph in CLI mode ---
    print("🔧 Building blog writing agent...")
    graph = build_graph(mode="cli")
    config = get_thread_config("cli_session_1")

    # --- Initial state ---
    initial_state: BlogState = {
        "topic": topic,
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

    # --- Run graph up to human review ---
    print(f"\n🚀 Starting blog agent for topic: '{topic}'\n")

    try:
        # Run graph — CLI mode goes research → draft → review → publish
        # Human review is injected manually between review and publish
        state = None

        for step in graph.stream(initial_state, config=config):
            node_name = list(step.keys())[0]
            node_state = step[node_name]

            print(f"\n✅ Completed: {node_name}")

            # --- After review node — inject human review ---
            if node_name == "review":
                state = node_state

                # Get human decision
                updated_state = get_human_review(state)
                decision = should_publish(updated_state)

                if decision == "end":
                    print("\n👋 Exiting without publishing. Goodbye!")
                    return

                elif decision == "draft":
                    # User wants revision — restart with feedback
                    print("\n🔄 Restarting with your feedback...\n")
                    updated_state["needs_revision"] = True
                    run_revision_loop(graph, updated_state, config)
                    return

                elif decision == "publish":
                    # User approved — continue to publish
                    print("\n📢 Publishing final blog...\n")
                    final_state = graph.invoke(
                        {**updated_state, "needs_revision": False},
                        config=get_thread_config("cli_session_publish")
                    )
                    display_final_blog(final_state)
                    return

    except Exception as e:
        print(f"\n❌ Error running agent: {str(e)}")
        sys.exit(1)


def run_revision_loop(graph, state, config):
    """
    Handles revision loop when human requests changes.
    """
    max_revisions = 3
    revision_count = state.get("revision_count", 0)

    while revision_count < max_revisions:
        print(f"\n🔄 Revision {revision_count + 1} of {max_revisions}...\n")

        # Run draft → review
        for step in graph.stream(state, config=config):
            node_name = list(step.keys())[0]
            node_state = step[node_name]
            print(f"✅ Completed: {node_name}")

            if node_name == "review":
                state = node_state
                updated_state = get_human_review(state)
                decision = should_publish(updated_state)

                if decision == "end":
                    print("\n👋 Exiting without publishing.")
                    return

                elif decision == "publish":
                    final_state = graph.invoke(
                        {**updated_state, "needs_revision": False},
                        config=get_thread_config(f"cli_revision_{revision_count}")
                    )
                    display_final_blog(final_state)
                    return

                elif decision == "draft":
                    state = updated_state
                    revision_count += 1
                    break

    print("\n⚠️  Max revisions reached. Publishing current version...")
    final_state = graph.invoke(
        {**state, "needs_revision": False},
        config=get_thread_config("cli_final")
    )
    display_final_blog(final_state)


def display_final_blog(state):
    """
    Displays the final published blog post.
    """
    final_blog = state.get("final_blog", "")

    if not final_blog:
        print("❌ No final blog generated.")
        return

    print_separator()
    print("🎉 FINAL BLOG POST — PUBLISHED!")
    print_separator()
    print(final_blog)
    print_separator()

    # --- Save to file ---
    save = input("💾 Save blog to file? (yes/no): ").strip().lower()
    if save == "yes":
        topic = state.get("topic", "blog").replace(" ", "_").lower()
        filename = f"{topic}_blog.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_blog)
        print(f"✅ Blog saved to {filename}")


if __name__ == "__main__":
    run_cli()