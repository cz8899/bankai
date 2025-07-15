# chatbot/utils/config_loader.py

import os
import json
import boto3
from botocore.exceptions import ClientError
from typing import Any, Optional
from chatbot.logger import logger

# === Environment Variables ===
CONFIG_FILE_PATH = os.getenv("DASHBOARD_CONFIG_PATH", "config/dashboard_config.json")
CONFIG_JSON_PATH = os.getenv("TUNING_CONFIG_PATH", "config/ai_tuning.json")
DYNAMO_TABLE = os.getenv("TUNING_CONFIG_TABLE", "devgenius_tuning_config")

# === Default Config ===
DEFAULT_CONFIG = {
    "chunk_score_threshold": 0.5,
    "rerank_top_k": 5,
    "embedding_engine": "bedrock",
    "summarization_tokens": 500
}


# === JSON Config ===
def load_config() -> dict:
    """
    Load user config from file, fallback to defaults.
    """
    if not os.path.exists(CONFIG_FILE_PATH):
        logger.warning("[Config] Config file not found. Using defaults.")
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            data = json.load(f)
        return {**DEFAULT_CONFIG, **data}
    except Exception as e:
        logger.warning(f"[Config] Failed to load config from file: {e}")
        return DEFAULT_CONFIG


def save_config(config: dict) -> bool:
    """
    Save current config to file.
    """
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
        with open(CONFIG_FILE_PATH, "w") as f:
            json.dump(config, f, indent=2)
        logger.info("[Config] Config saved successfully.")
        return True
    except Exception as e:
        logger.error(f"[Config] Failed to save config: {e}")
        return False


def get_config_value(key: str, default: Optional[Any] = None) -> Any:
    """
    Read single config value from current config.
    """
    config = load_config()
    return config.get(key, default)


# === Advanced Tuning Config (JSON or DynamoDB) ===
def load_tuning_config(source: str = "json") -> dict:
    """
    Load tuning config either from JSON file or DynamoDB.
    """
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
            logger.error(f"[ConfigLoader] DynamoDB fallback: {e}")
            return {}
    else:
        try:
            with open(CONFIG_JSON_PATH) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[ConfigLoader] JSON fallback: {e}")
            return {}


def save_tuning_config(config: dict, target: str = "json") -> bool:
    """
    Save tuning config to JSON or DynamoDB.
    """
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
            logger.info("[ConfigSaver] Saved to DynamoDB.")
            return True
        except ClientError as e:
            logger.error(f"[ConfigSaver] DynamoDB error: {e}")
            return False
    else:
        try:
            os.makedirs(os.path.dirname(CONFIG_JSON_PATH), exist_ok=True)
            with open(CONFIG_JSON_PATH, "w") as f:
                json.dump(config, f, indent=2)
            logger.info("[ConfigSaver] Saved to local JSON.")
            return True
        except Exception as e:
            logger.error(f"[ConfigSaver] JSON error: {e}")
            return False
