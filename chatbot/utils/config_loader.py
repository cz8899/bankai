# chatbot/utils/config_loader.py
import json
import os
import boto3
from botocore.exceptions import ClientError
from typing import Any, Optional
from chatbot.logger import logger

CONFIG_JSON_PATH = os.getenv("TUNING_CONFIG_PATH", "config/ai_tuning.json")
DYNAMO_TABLE = os.getenv("TUNING_CONFIG_TABLE", "devgenius_tuning_config")
CONFIG_FILE_PATH = os.getenv("DASHBOARD_CONFIG_PATH", "config/dashboard_config.json")

# Default fallback config
DEFAULT_CONFIG = {
    "chunk_score_threshold": 0.5,
    "rerank_top_k": 5,
    "embedding_engine": "bedrock",
    "summarization_tokens": 500
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE_PATH):
        logger.warning(f"[Config] Config file not found, using defaults.")
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            data = json.load(f)
        return {**DEFAULT_CONFIG, **data}
    except Exception as e:
        logger.warning(f"[Config] Failed to load config: {e}")
        return DEFAULT_CONFIG


def save_config(config: dict) -> bool:
    try:
        with open(CONFIG_FILE_PATH, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"[Config] Updated configuration saved.")
        return True
    except Exception as e:
        logger.error(f"[Config] Failed to write config: {e}")
        return False


def get_config_value(key: str, default: Optional[Any] = None) -> Any:
    config = load_config()
    return config.get(key, default)

def load_tuning_config(source="json") -> dict:
    if source == "dynamo":
        try:
            ddb = boto3.client("dynamodb")
            response = ddb.get_item(
                TableName=DYNAMO_TABLE,
                Key={"config_id": {"S": "default"}}
            )
            item = response.get("Item")
            return json.loads(item["payload"]["S"]) if item else {}
        except ClientError as e:
            print(f"[ConfigLoader] DynamoDB fallback: {e}")
            return {}
    else:
        try:
            with open(CONFIG_JSON_PATH) as f:
                return json.load(f)
        except Exception as e:
            print(f"[ConfigLoader] JSON fallback: {e}")
            return {}


def save_tuning_config(config: dict, target="json") -> bool:
    if target == "dynamo":
        try:
            ddb = boto3.client("dynamodb")
            ddb.put_item(
                TableName=DYNAMO_TABLE,
                Item={
                    "config_id": {"S": "default"},
                    "payload": {"S": json.dumps(config)}
                }
            )
            return True
        except ClientError as e:
            print(f"[ConfigSaver] DynamoDB error: {e}")
            return False
    else:
        try:
            with open(CONFIG_JSON_PATH, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"[ConfigSaver] JSON error: {e}")
            return False
