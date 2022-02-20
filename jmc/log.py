import logging
from pathlib import Path
from enum import Enum, auto
from sys import argv

from .config import configs

FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

FILE_PATH = Path(argv[0]).parent/'jmc.log'

DEBUG_MODE = configs["debug_mode"]

if DEBUG_MODE and FILE_PATH.exists():
    FILE_PATH.unlink()

class Colors(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m' 
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color_print(text: str, color: Colors = Colors.FAIL):
    print(color.value + str(text) + '\033[0m')

class Logger(logging.Logger):
    Colors = Colors
    @classmethod
    def color_print(text: str, color: Colors = Colors.FAIL) -> None:
        color_print(text, color)

def Logger(name: str) -> Logger:
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

    logger.Colors = Colors

    logger.color_print = color_print

    return logger


logger = Logger(__name__)
logger.info('Version: v1.1.12')
