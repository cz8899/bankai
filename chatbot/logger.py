# chatbot/logger.py

import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# === Setup Log Directory ===
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# === Environment Log Level ===
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
if LOG_LEVEL not in VALID_LOG_LEVELS:
    LOG_LEVEL = "INFO"

# === Global Logger Instance ===
logger = logging.getLogger("devgenius")

if not logger.handlers:
    logger.setLevel(LOG_LEVEL)

    # === Console Handler ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s — %(levelname)s — %(message)s"
    ))
    logger.addHandler(console_handler)

    # === Rotating File Handler ===
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s — %(levelname)s — %(message)s"
    ))
    logger.addHandler(file_handler)

    # === Prevent Double Logging ===
    logger.propagate = False

    # === Startup Banner ===
    logger.info("🔁 Logger initialized")
    logger.info(f"📓 Logging level: {LOG_LEVEL}")
