import re
from . import Logger, PackGlobal
import logging

logger = Logger(__name__, logging.INFO)


class Command:
    def __init__(self, text: str, pack_global: PackGlobal) -> None:
        self.text = text
        logger.debug(f"""Command created: 
        Text: {self.text}""")

    def __str__(self) -> str:
        return self.text
