import re
from . import Logger, PackGlobal
import logging
from .utils import replace_function_call

logger = Logger(__name__)


class Command:
    """Datapack function command"""

    def __init__(self, text: str, pack_global: PackGlobal) -> None:
        self.text = replace_function_call(text, pack_global)
        logger.debug(f"""Command created: 
        Text: {self.text}""")

    def __str__(self) -> str:
        return self.text
