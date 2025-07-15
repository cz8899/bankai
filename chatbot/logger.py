import logging
import sys
from pathlib import Path

# Global logger instance
logger = logging.getLogger("devgenius")

# Avoid duplicate handlers if module is re-imported
if not logger.handlers:
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
    )
    logger.addHandler(console_handler)

    # Optional: Add file logging
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(LOG_DIR / "app.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
    )
    logger.addHandler(file_handler)

    logger.propagate = False  # Prevent log duplication to root logger
