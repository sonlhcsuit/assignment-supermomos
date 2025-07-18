"""Logging configuration and management.

This module provides a centralized logging setup using loguru and
standard library logging. It includes a custom logger class, a method
to set up logging, and a function to retrieve logger instances.
It also includes a custom logging handler to intercept standard library
logging and redirect it to loguru.
"""

import inspect
import logging
import logging.config
import logging.handlers
import sys
from datetime import UTC, datetime
from pathlib import Path

import asgi_correlation_id
from loguru import logger

from src.core.config import settings


class CustomLogger:
    """Centralized logging configuration and management."""

    def __init__(self):
        self._setup_loguru_logger()
        self._configure_logging()

    def _setup_loguru_logger(self):
        """Configure loguru logger with correlation ID and formatting."""
        fmt = (
            '{time:YYYY-MM-DD HH:mm:ss} | '
            '{level: <8} | '
            '{correlation_id: <20} | '
            '{name}:{function}:{line} - '
            '{message}'
        )

        # Clear existing handlers
        logger.remove()
        # Add stderr handler with custom format
        logger.add(
            sys.stderr,
            format=fmt,
            level=settings.LOG_LEVEL,
            filter=self._correlation_id_filter,
        )
        # Add file handler
        logger.add(
            self._get_log_file_path(),
            format=fmt,
            level='WARNING',
            rotation='1 day',
            retention='30 days',
            filter=self._correlation_id_filter,
        )

    @staticmethod
    def _correlation_id_filter(record):
        """Add correlation ID to log records."""
        correlation_id = asgi_correlation_id.context.correlation_id.get()
        record['correlation_id'] = correlation_id or 'no-correlation-id'
        return True

    @staticmethod
    def _get_log_file_path() -> Path:
        """Generate log file path with date-based naming."""
        log_dir = Path(settings.LOG_OUTPUT)
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / f'{datetime.now(tz=UTC).strftime("%Y%m%d")}.log'

    def _configure_logging(self):
        """Configure standard library logging to use loguru."""
        logging.config.dictConfig(
            {
                'version': 1,
                'disable_existing_loggers': False,
                'handlers': {
                    'loguru': {
                        'class': __name__ + '.InterceptHandler',
                    },
                },
                'root': {
                    'handlers': ['loguru'],
                    'level': settings.LOG_LEVEL,
                },
                # Specific logger configurations
                'loggers': {
                    'uvicorn': {
                        'handlers': ['loguru'],
                        'level': 'WARNING',
                        'propagate': False,
                    },
                    'uvicorn.access': {
                        'handlers': ['loguru'],
                        'level': settings.LOG_LEVEL,
                        'propagate': False,
                    },
                    'uvicorn.error': {
                        'handlers': ['loguru'],
                        'level': 'ERROR',
                        'propagate': False,
                    },
                    'httpx': {'handlers': ['loguru'], 'level': 'ERROR'},
                    'urllib3': {'handlers': ['loguru']},
                },
            },
        )


class InterceptHandler(logging.Handler):
    """Intercept standard library logging and redirect to loguru."""

    def emit(self, record: logging.LogRecord):
        # Skip INFO level messages from logging:callHandlers
        if record.levelno == logging.INFO and record.name == 'logging' and 'callHandlers' in record.pathname:
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


# Singleton instance
_logger_instance: CustomLogger | None = None


def setup_logging():
    """Initialize the logging system."""
    global _logger_instance  # noqa: PLW0603
    if _logger_instance is None:
        _logger_instance = CustomLogger()


def get_logger(name: str | None = None):
    """Get a logger instance.

    Args:
        name: Optional name for the logger. If not provided, automatically detects the calling module's name.

    Returns:
        A configured logger instance
    """
    if name is None:
        # Get the calling module's name
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        module_name = inspect.getmodule(caller_frame).__name__
        name = module_name

    return logger.bind(name=name)
