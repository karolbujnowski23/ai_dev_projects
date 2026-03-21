import logging
import sys
from src.config import LOG_LEVEL

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # File Handler
    fh = logging.FileHandler('agent.log', encoding='utf-8')
    fh.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

log = setup_logger("mcp-template")
