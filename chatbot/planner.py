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
        LLM response string
    """
    user_input = messages[-1]["content"]
    intent = route_prompt(user_input)
    logger.info(f"[Planner] User intent routed as: {intent}")

    # === Stage Advancement ===
    current_stage = st.session_state.get("planner_stage", "gathering_requirements")
    try:
        if "confirm" in intent.lower():
            st.session_state.planner_stage = "final_confirmation"
        elif "generate" in intent.lower():
            st.session_state.planner_stage = "generating_solution"
        elif "architecture" in intent.lower():
            st.session_state.planner_stage = "showing_widgets"
        else:
            next_stage_idx = PLANNER_STAGES.index(current_stage) + 1
            if next_stage_idx < len(PLANNER_STAGES):
                st.session_state.planner_stage = PLANNER_STAGES[next_stage_idx]
            else:
                logger.debug("[Stage] Already at final stage: %s", current_stage)
    except Exception as e:
        logger.warning("[Stage] Fallback to default stage due to error: %s", str(e))
        st.session_state.planner_stage = "gathering_requirements"

    # === Mode Routing ===
    try:
        if mode == "Claude":
            logger.info("[Planner] Mode: Claude")
            return call_claude(user_input)

        elif mode == "Agent":
            logger.info("[Planner] Mode: Bedrock Agent")
            session_id = st.session_state.get("agent_session_id") or f"session-{st.session_state.get('conversation_id', 'anon')}"
            st.session_state.agent_session_id = session_id

            agent_response = call_bedrock_agent(user_input, session_id=session_id)
            if "[Agent returned no message]" in agent_response:
                logger.warning("[Planner] Agent failed, falling back to Claude")
                st.warning("⚠️ Agent failed — falling back to Claude.")
                return call_claude(user_input)
            return agent_response

        elif mode == "RAG+Chunks":
            logger.info("[Planner] Mode: RAG+Chunks")
            try:
                chunks = hybrid_rag_router(user_input)
                if not chunks:
                    logger.warning("[RAG] No relevant chunks found — falling back to Claude")
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
                logger.exception("[RAG] Retrieval failed, fallback to Claude: %s", str(rag_error))
                return call_claude(user_input)

        else:
            logger.warning(f"[Planner] Unknown mode received: '{mode}'")
            return f"❓ Unknown mode '{mode}'. Please try again."

    except Exception as e:
        logger.exception("Planner failed during mode routing: %s", str(e))
        return "⚠️ Sorry, an error occurred while planning your request."
