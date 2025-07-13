# chatbot/utils/constants.py

import os

# === Branding and UI Colors ===
TRUIST_PURPLE = "#512B8B"
TRUIST_GREY = "#F3F2F1"
TRUIST_FONT = "'Segoe UI', sans-serif"
TRUIST_SHADOW = "rgba(81, 43, 139, 0.2)"
LOGO_PATH = "chatbot/assets/tfc_logo.png"

# SMTP Fallback
SMTP_SERVER = "smtp.yourbank.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "alerts@yourbank.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-password")  # Use env vars in prod

# Email Alert Settings
ALERT_EMAIL_FROM = "alerts@yourdomain.com"     # Must be verified in SES
ALERT_EMAIL_TO = "cloudaiops@yourbank.com"
AWS_REGION = "us-west-2"

# === App Metadata ===
APP_NAME = "DevGenius AI Co-Pilot"
ORG_NAME = "Truist"
SUPPORT_EMAIL = "support@truist.com"

# === Claude & Bedrock ===
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
BEDROCK_REGION = os.getenv("AWS_REGION", "us-west-2")

# === Bedrock Knowledge Base (optional) ===
BEDROCK_KB_ID = os.getenv("BEDROCK_KB_ID", "your-bedrock-kb-id")  # Replace in prod
BEDROCK_KB_INDEX = "default-index"

# === Limits & RAG ===
MAX_CHUNKS = 10
MAX_HISTORY = 20
CHUNK_OVERLAP = 40
CHUNK_SIZE = 300  # tokens

# === Cost Constants (USD per 1K tokens or per call) ===
COST_PER_1K_CLAUDE_INPUT = 0.008
COST_PER_1K_CLAUDE_OUTPUT = 0.024
COST_PER_RETRIEVAL = 0.001
COST_TRACKING_ENABLED = True

# === Paths (overrideable for dev or local logging) ===
LOGS_DIR = os.getenv("LOGS_DIR", "logs")
INTERACTIONS_LOG_PATH = os.getenv("INTERACTIONS_LOG_PATH", f"{LOGS_DIR}/interactions.jsonl")
CHUNK_DB_PATH = os.getenv("CHUNK_DB_PATH", "storage/chunk_index.json")
KNOWLEDGE_JSON_PATH = os.getenv("KNOWLEDGE_JSON_PATH", "storage/kb_metadata.json")

# === System Message for Claude ===
SYSTEM_MESSAGE = """
You are DevGenius AI, a solution design assistant for complex enterprise cloud apps.
Help the user clarify what they're trying to build before you offer a solution.
Use Socratic questioning, ask clarifying questions, and confirm when ready to move to design.
"""

# === Planner Stages (state machine flow) ===
PLANNER_STAGES = [
    "gathering_requirements",
    "refining_scope",
    "final_confirmation",
    "generating_solution",
    "showing_widgets"
]
