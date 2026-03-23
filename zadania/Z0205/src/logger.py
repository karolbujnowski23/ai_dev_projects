import logging
import os

os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'logs'), exist_ok=True)

logger = logging.getLogger("App")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'app.log'))
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
