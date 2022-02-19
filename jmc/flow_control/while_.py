import regex
import re
from typing import TYPE_CHECKING

from ..utils import BracketRegex
from .condition import Condition
from .function_ import Function
from .. import Logger

if TYPE_CHECKING:
    from ..datapack import DataPack

logger = Logger(__name__)

bracket_regex = BracketRegex()
WHILE_REGEX = f"^while\\s*{bracket_regex.match_bracket('()', 1)}\\s*{bracket_regex.match_bracket('{}', 2)}"


def capture_while(self: "DataPack", line: str) -> tuple[str, bool]:
    line = line.strip()

    def while_found(match: re.Match):
        logger.debug("While found")
        groups = bracket_regex.compile(match.groups())
        return handle_while(self, groups)

    line, success = regex.subn(WHILE_REGEX, while_found, line, count=1)

    return line, success


def handle_while(datapack: "DataPack", groups: tuple[str]) -> str:
    logger.debug("Handling While Loop")
    condition = Condition(groups[0])
    count = datapack.get_pfc("while_loop")
    datapack.private_functions["while_loop"][count] = Function(datapack.process_function_content(
        f"{groups[1]} {condition.pre_commands}execute{condition} run function {datapack.namespace}:__private__/while_loop/{count};"))

    return f'{condition.pre_commands}execute{condition} run function {datapack.namespace}:__private__/while_loop/{count};'
