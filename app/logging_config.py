import json
import logging
import os
import traceback
from datetime import datetime, timezone
from fastapi import Request

# Ensure logs directory exists relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOGS_DIR, "app.log")

logger = logging.getLogger("sentinelops-patient")
logger.setLevel(logging.INFO)


def log_exception_event(request: Request, exc: Exception) -> dict:
    """
    Structured error logging for unhandled exceptions.
    Appends a JSON line to logs/app.log for easy automated parsing by AI agents.
    """
    error_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "path": request.url.path,
        "exception_type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc()
    }

    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_payload) + "\n")
    except Exception as io_err:
        logger.error(f"Failed writing to {LOG_FILE_PATH}: {io_err}")

    return error_payload
