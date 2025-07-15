# chatbot/utils/config_loader.py
import json
import os
import boto3
from botocore.exceptions import ClientError

CONFIG_JSON_PATH = os.getenv("TUNING_CONFIG_PATH", "config/ai_tuning.json")
DYNAMO_TABLE = os.getenv("TUNING_CONFIG_TABLE", "devgenius_tuning_config")


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
