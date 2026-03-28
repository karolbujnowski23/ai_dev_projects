import logging
import os
import sys

# Upewnij się, że folder na logi istnieje
os.makedirs('logs', exist_ok=True)

# Konfiguracja głównego loggera
logger = logging.getLogger("App")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handler do pliku
file_handler = logging.FileHandler("logs/app.log", encoding='utf-8')
file_handler.setFormatter(formatter)

# Handler do konsoli
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class LoggerWrapper:
    def info(self, msg):
        logger.info(msg)
        
    def error(self, msg):
        logger.error(msg)
        
    def success(self, msg):
        logger.info(f"[SUCCESS] {msg}")
        
    def box(self, msg):
        logger.info(f"\n{'='*len(msg)}\n{msg}\n{'='*len(msg)}")

log = LoggerWrapper()