"""Logging configuration — structured JSON in production, readable in dev."""

import logging
import sys

from src.config.settings import settings


def setup_logging() -> None:
    """Call once at app startup (in main.py lifespan)."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.app_env == "production":
        # JSON format for log aggregators (Datadog, CloudWatch, Loki, etc.)
        try:
            import structlog  # optional dep — add structlog to requirements.txt
            structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(log_level),
                logger_factory=structlog.PrintLoggerFactory(sys.stdout),
            )
        except ImportError:
            # Fall back to standard logging if structlog not installed
            _configure_standard(log_level)
    else:
        _configure_standard(log_level)


def _configure_standard(log_level: int) -> None:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Preferred way to get a logger in any module: logger = get_logger(__name__)"""
    return logging.getLogger(name)
