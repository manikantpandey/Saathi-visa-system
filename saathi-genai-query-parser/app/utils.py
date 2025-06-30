import logging
import time
from typing import Callable, Any

logger = logging.getLogger("saathi-genai-query-parser.utils")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_message(message: str, level: str = "info"):
    """
    Log messages for debugging and tracking.
    """
    level = level.lower()
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.debug(message)

def retry(func: Callable[[], Any], retries: int = 3, delay: int = 2) -> Any:
    """
    Retry a given function with specified retries and delay.
    """
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            log_message(f"Attempt {attempt} failed: {e}", level="warning")
            if attempt < retries:
                time.sleep(delay)
    log_message("All retry attempts failed", level="error")
    raise last_exception if last_exception else Exception("All retry attempts failed")