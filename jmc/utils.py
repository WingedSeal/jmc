import logging
import re
from . import Logger

logger = Logger(__name__, logging.INFO)


def clean_whitespace(string: str) -> str:
    logger.info("Cleaning whitespace")
    return re.sub(r"\s+", " ", string)
