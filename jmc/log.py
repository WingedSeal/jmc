import logging
from pathlib import Path
from sys import argv

from .config import configs

FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

FILE_PATH = Path(argv[0]).parent/'jmc.log'

DEBUG_MODE = configs["debug_mode"]

if DEBUG_MODE and FILE_PATH.exists():
    FILE_PATH.unlink()


def Logger(name: str) -> logging.Logger:
    """```python
    logger = Logger(__name__)
    ```"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(FORMATTER)
    logger.addHandler(stream_handler)

    if DEBUG_MODE:
        FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(FILE_PATH.resolve())
        file_handler.setFormatter(FORMATTER)
        logger.addHandler(file_handler)

    return logger


logger = Logger(__name__)
logger.info('Version: v1.1.2')
