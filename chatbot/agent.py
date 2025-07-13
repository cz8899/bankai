# chatbot/agent.py

import boto3, json
from chatbot.utils.constants import CLAUDE_MODEL_ID, BEDROCK_REGION
from chatbot.ranking import rank_chunks_by_similarity

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def call_claude(messages):
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7,
    }
    response = bedrock.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        contentType="application/json",
        body=json.dumps(payload)
    )
    completion = json.loads(response["body"].read())
    return completion["content"]

def call_agent(agent_id, input_text):
    return "[Stubbed Agent Response]"

def get_ranked_chunks(query, all_chunks):
    return rank_chunks_by_similarity(query, all_chunks)[:5]
