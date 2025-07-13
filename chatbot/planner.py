# chatbot/planner.py

from chatbot.utils.prompt_router import route_prompt
from chatbot.agent import call_claude, call_bedrock_agent
from chatbot.rag.retrieval_layer import get_relevant_chunks
from chatbot.logger import logger


def planner(messages: list[dict], mode: str = "Claude") -> str:
    """
    Central planning hub that decides how to process user input.

    Args:
        messages: Full conversation history.
        mode: 'Claude' | 'Agent' | 'RAG+Chunks'

    Returns:
        string response
    """
    user_input = messages[-1]["content"]
    intent = route_prompt(user_input)

    # Save planner stage to session
    if "generate" in intent.lower():
        from streamlit import session_state as st_session
        st_session.planner_stage = "showing_widgets"

    try:
        if mode == "Claude":
            return call_claude(user_input)

        elif mode == "Agent":
            return call_bedrock_agent(user_input)

        elif mode == "RAG+Chunks":
            chunks = get_relevant_chunks(user_input)
            context = "\n".join(chunk["content"] for chunk in chunks)
            return call_claude(f"Use this context:\n{context}\n\n{user_input}")

        else:
            return f"❓ Unknown mode '{mode}'. Please try again."

    except Exception as e:
        logger.exception("Planner failed: %s", str(e))
        return "⚠️ Sorry, an error occurred while planning your request."
