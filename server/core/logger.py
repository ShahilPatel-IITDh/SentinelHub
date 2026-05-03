import logging

logger = logging.getLogger("sentinel")
logger.setLevel(logging.INFO)

# Format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

# File handler (THIS is important)
file_handler = logging.FileHandler("server.log")
file_handler.setFormatter(formatter)

# Console handler (optional but useful)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Avoid duplicate logs
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)