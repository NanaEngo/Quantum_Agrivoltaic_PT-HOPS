"""
Unified Logging and Observability Framework.

This module provides a centralized configuration for the simulation's logging
subsystem. It ensures that all components across the
`quantum_simulations_framework` hierarchy use a consistent format,
log level, and persistence strategy (file + console).
"""

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
    """
    Initialize the global logging state for the simulation framework.

    Sets up handlers for both console (INFO) and file (DEBUG) output with
    rotation, defines the formatting template, and sets the base log level.

    Parameters
    ----------
    level : int
        Base log level (default: INFO).
    log_file : str, optional
        Filesystem path to the target log file. If None, file logging disabled.
    log_to_console : bool
        If True, directs logs to stdout. Default is True.
    format_string : str, optional
        Custom formatting template.
    file_level : int, optional
        Log level for file handler (default: DEBUG for more detail on disk).
    max_bytes : int
        Max size per log file before rotation (default: 10 MB).
    backup_count : int
        Number of rotated log files to keep (default: 5).

    Returns
    -------
    logging.Logger
        The root package-level logger.
    """
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"

    formatter = logging.Formatter(format_string, datefmt="%H:%M:%S")

    logger = logging.getLogger("quantum_simulations_framework")
    logger.setLevel(level)
    logger.handlers = []

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(lambda r: r.levelno >= level)
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
    """
    Get a logger instance for a specific module.

    Parameters
    ----------
    name : str
        The name of the module (typically __name__)

    Returns
    -------
    logging.Logger
        A logger instance with the specified name.

    Examples
    --------
    >>> from utils.logging_config import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("Module initialized")
    """
    return logging.getLogger(f"quantum_simulations_framework.{name}")


class SimulationLogMixin:
    """
    Mixin class to add logging capability to simulation classes.

    Automatically creates a logger instance based on the class name.
    """

    def __init__(self):
        self._logger = logging.getLogger(
            f"quantum_simulations_framework.{self.__class__.__module__}.{self.__class__.__name__}"
        )

    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance for this class."""
        return self._logger

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    def log_info(self, message: str) -> None:
        """Log an info message."""
        self._logger.info(message)

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)

    def log_error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)
