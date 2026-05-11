"""
Unified Logging and Observability Framework.

This module provides a centralized configuration for the simulation's logging 
subsystem. It ensures that all components across the 
`quantum_simulations_framework` hierarchy use a consistent format, 
log level, and persistence strategy (file + console).
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Initialize the global logging state for the simulation framework.

    This function sets up handlers for both console and file output, defines 
    the formatting template, and sets the base log level. It is typically 
    called once at the entry point of the application (e.g., in main.py).

    Parameters
    ----------
    level : int, optional
        The threshold for logging events (e.g., logging.DEBUG, logging.INFO). 
        Default is logging.INFO.
    log_file : str, optional
        Filesystem path to the target log file. If None, only console 
        logging is active.
    log_to_console : bool, optional
        If True, directs logs to stdout. Default is True.
    format_string : str, optional
        A custom strftime-style formatting template. If None, a standard 
        package-level format is applied.

    Returns
    -------
    logging.Logger
        The root package-level logger.

    Notes
    -----
    This implementation clears any existing handlers on the 
    `quantum_simulations_framework` logger to prevent duplicated messages 
    during repeated configuration calls.
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Get the package logger
    logger = logging.getLogger("quantum_simulations_framework")
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
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
