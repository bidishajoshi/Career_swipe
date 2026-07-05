import logging
import sys

def get_logger(name: str = "career_swipe") -> logging.Logger:
    """Return a configured logger that outputs to the console with a consistent format.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Module-level logger for convenience
logger = get_logger()
