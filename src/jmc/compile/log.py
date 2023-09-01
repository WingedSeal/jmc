"""Module handling logging"""
from io import StringIO
import logging

debug_log_stream = StringIO()
info_log_stream = StringIO()
FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')


def get_info_log() -> str:
    """Return log string"""
    return info_log_stream.getvalue()


def get_debug_log() -> str:
    """Return log string"""
    return debug_log_stream.getvalue()


def Logger(name: str) -> logging.Logger:
    """Usage:
    ```python
    logger = Logger(__name__)
    ```"""

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(debug_log_stream)
    stream_handler.setFormatter(FORMATTER)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    stream_handler = logging.StreamHandler(info_log_stream)
    stream_handler.setFormatter(FORMATTER)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    logger.propagate = False
    return logger
