import logging
import os
import time

def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    logger = logging.getLogger('windpower')
    logger.setLevel(logging.DEBUG)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # File Handler for ALL raw JSON responses
    fh = logging.FileHandler(f'logs/api_responses_{int(time.time())}.log')
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(fh_formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
    
    return logger

logger = setup_logger()
