import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    format_string: Optional[str] = None,
    file_level: Optional[int] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"

    formatter = logging.Formatter(format_string, datefmt="%H:%M:%S")

    logger = logging.getLogger("Redac_Paper2")
    logger.setLevel(level)
    logger.handlers = []

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(file_level or logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"Redac_Paper2.{name}")
