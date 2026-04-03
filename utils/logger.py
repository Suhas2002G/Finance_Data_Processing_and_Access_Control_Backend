from loguru import logger
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


def setup_logger():
    # Remove default logger (important to avoid duplicates)
    logger.remove()

    # Console logger
    logger.add(
        sys.stdout,
        level="INFO",
        format=""
               "<level>{level}</level> | "
               "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
    )

    # File logger
    logger.add(
        LOG_FILE,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )

    return logger