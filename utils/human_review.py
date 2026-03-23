def get_human_review(state: dict) -> dict:
    """
    Human-in-the-loop helper.
    Called between review_node and publish_node.

    In Streamlit — handled directly in streamlit_app.py via buttons.
    In CLI — handled here via terminal input.

    Reads:  state["blog_draft"]
            state["review_feedback"]
            state["review_score"]
    Writes: state["human_approved"]
            state["human_feedback"]
            state["current_node"]
    """
    blog_draft = state.get("blog_draft", "")
    review_feedback = state.get("review_feedback", "")
    review_score = state.get("review_score", 0)

    print("\n" + "=" * 60)
    print("👤  HUMAN REVIEW — Your input is needed")
    print("=" * 60)
    print(f"\n📊 AI Review Score: {review_score}/10\n")
    print("─" * 60)
    print("\n📝 BLOG DRAFT:\n")
    print(blog_draft)
    print("\n" + "─" * 60)
    print("\n🔎 AI REVIEW FEEDBACK:\n")
    print(review_feedback)
    print("\n" + "=" * 60)

    while True:
        print("\nWhat would you like to do?")
        print("  1. Approve — publish as is")
        print("  2. Revise  — send back for changes")
        print("  3. Quit    — exit without publishing")

        choice = input("\nYour choice (1/2/3): ").strip()

        if choice == "1":
            print("\n✅ Blog approved! Sending to publish...")
            return {
                **state,
                "human_approved": True,
                "human_feedback": None,
                "current_node": "human_review"
            }

        elif choice == "2":
            print("\n💬 What changes would you like?")
            print("(Be specific — the AI will rewrite based on your feedback)\n")
            feedback = input("Your feedback: ").strip()

            if not feedback:
                print("⚠️  Please provide feedback for revision.")
                continue

            print(f"\n🔄 Sending back for revision with your feedback...")
            return {
                **state,
                "human_approved": False,
                "human_feedback": feedback,
                "current_node": "human_review"
            }

        elif choice == "3":
            print("\n👋 Exiting without publishing.")
            return {
                **state,
                "human_approved": False,
                "human_feedback": "User chose to quit.",
                "current_node": "human_review"
            }

        else:
            print("⚠️  Invalid choice. Please enter 1, 2, or 3.")


def should_publish(state: dict) -> str:
    """
    Conditional edge function.
    Called after human_review to decide next node.

    Returns:
        "publish"  → if human approved
        "draft"    → if human wants revision
        "end"      → if user quit
    """
    human_approved = state.get("human_approved", False)
    human_feedback = state.get("human_feedback", "")

    if human_approved:
        return "publish"
    elif human_feedback == "User chose to quit.":
        return "end"
    else:
        return "draft"


def should_revise(state: dict) -> str:
    """
    Conditional edge function.
    Called after review_node to decide next node.

    Returns:
        "human_review" → if AI score is good enough
        "draft"        → if AI score is too low
    """
    needs_revision = state.get("needs_revision", False)

    if needs_revision:
        return "draft"
    else:
        return "human_review"