# chatbot/planner.py

import streamlit as st
from chatbot.utils.prompt_router import route_prompt
from chatbot.agent import call_claude, call_bedrock_agent
from chatbot.rag.rag_router import hybrid_rag_router
from chatbot.logger import logger
from chatbot.utils.constants import PLANNER_STAGES


def planner(messages: list[dict], mode: str = "Claude") -> str:
    """
    Central planning hub that decides how to process user input.

    Args:
        messages: Full conversation history.
        mode: Claude | Agent | RAG+Chunks

    Returns:
        string LLM response
    """

    user_input = messages[-1]["content"]
    intent = route_prompt(user_input)

    # === Stage Advancement ===
    current_stage = st.session_state.get("planner_stage", "gathering_requirements")
    if "confirm" in intent.lower():
        st.session_state.planner_stage = "final_confirmation"
    elif "generate" in intent.lower():
        st.session_state.planner_stage = "generating_solution"
    elif "architecture" in intent.lower():
        st.session_state.planner_stage = "showing_widgets"
    else:
        try:
            idx = PLANNER_STAGES.index(current_stage)
            if idx + 1 < len(PLANNER_STAGES):
                st.session_state.planner_stage = PLANNER_STAGES[idx + 1]
        except ValueError:
            st.session_state.planner_stage = "gathering_requirements"

    # === Mode Routing ===
    try:
        if mode == "Claude":
            return call_claude(user_input)

        elif mode == "Agent":
            session_id = st.session_state.get("agent_session_id")
            if not session_id:
                session_id = f"session-{st.session_state.conversation_id}"
                st.session_state.agent_session_id = session_id

            agent_response = call_bedrock_agent(user_input, session_id=session_id)

            if "[Agent returned no message]" in agent_response:
                st.warning("⚠️ Agent failed — falling back to Claude.")
                return call_claude(user_input)

            return agent_response

        elif mode == "RAG+Chunks":
            try:
                chunks = hybrid_rag_router(user_input)
                if not chunks:
                    logger.warning("[RAG] No relevant chunks found. Falling back to Claude.")
                    return call_claude(user_input)

                context = "\n\n".join(
                    f"[{c['metadata'].get('title', 'Doc')}] "
                    f"(Page {c['metadata'].get('page', '?')}) "
                    f"from {c['metadata'].get('source', 'Unknown')}:\n{c['content']}"
                    for c in chunks
                )

                st.session_state.rag_sources_used = list({
                    c['metadata'].get('source', 'Unknown') for c in chunks
                })

                combined_prompt = f"""Here is helpful context:\n\n{context}\n\nNow answer this:\n{user_input}"""
                return call_claude(combined_prompt)

            except Exception as rag_error:
                logger.exception("[RAG] Retrieval failed: %s", str(rag_error))
                return call_claude(user_input)


        else:
            return f"❓ Unknown mode '{mode}'. Please try again."

    except Exception as e:
        logger.exception("Planner failed: %s", str(e))
        return "⚠️ Sorry, an error occurred while planning your request."
