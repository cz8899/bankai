# chatbot/agent.py

import json
import boto3
from typing import List, Dict, Optional
from chatbot.utils.constants import (
    BEDROCK_MODEL_ID,
    BEDROCK_REGION,
    BEDROCK_AGENT_ID,
    BEDROCK_AGENT_ALIAS_ID,
    SYSTEM_MESSAGE,
    MAX_CHUNKS
)
from chatbot.ranking import rank_chunks_by_similarity
from chatbot.logger import logger


# Bedrock clients
bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
agent_runtime = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)


def call_claude(user_input: str, context: str = "") -> str:
    """
    Calls Claude 3 Sonnet on Bedrock with optional RAG context.
    """
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": f"{context}\n\n{user_input}".strip()}
    ]

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        body = json.loads(response["body"].read())
        return body.get("content", "[Claude returned no content]")

    except Exception as e:
        logger.exception("Claude invocation failed")
        return f"⚠️ Claude error: {str(e)}"


def call_bedrock_agent(user_input: str, session_id: Optional[str] = None) -> str:
    """
    Invokes a Bedrock Agent via InvokeAgent.
    """
    if not session_id:
        session_id = "session-" + str(hash(user_input))

    try:
        response = agent_runtime.invoke_agent(
            agentId=BEDROCK_AGENT_ID,
            agentAliasId=BEDROCK_AGENT_ALIAS_ID,
            sessionId=session_id,
            input={"text": user_input}
        )

        # Decode streamed agent response body
        body = response.get("completion", {}).get("content")
        if body:
            content = json.loads(body)
            return content.get("message", "[Agent returned no message]")
        else:
            return "[Agent returned no message]"

    except Exception as e:
        logger.exception("Bedrock Agent invocation failed")
        return f"⚠️ Agent error: {str(e)}"


def get_ranked_chunks(query: str, all_chunks: List[Dict]) -> List[Dict]:
    """
    Return top-N relevant chunks using vector similarity.
    """
    return rank_chunks_by_similarity(query, all_chunks)[:MAX_CHUNKS]
