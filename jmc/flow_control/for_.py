import regex
import re
from typing import TYPE_CHECKING

from ..utils import BracketRegex, split, Re
from .condition import Condition
from .function_ import Function
from .. import Logger

if TYPE_CHECKING:
    from ..datapack import DataPack

logger = Logger(__name__)

bracket_regex = BracketRegex()
FOR_REGEX = f"for\s*{bracket_regex.match_bracket('()', 1)}\s*{bracket_regex.match_bracket('{}', 2)}"


def capture_for(self: "DataPack", line: str) -> tuple[str, bool]:
    line = line.strip()

    def for_found(match: re.Match):
        logger.debug("For found")
        groups = bracket_regex.compile(match.groups())
        return handle_for(self, groups)
    line, success = regex.subn(FOR_REGEX, for_found, line, count=1)

    return line, success


def handle_for(datapack: "DataPack", groups: tuple[str]) -> str:
    statements = split(groups[0], ';')
    match = regex.match(
        f'let\s*{Re.var_nosigncap}\s*=\s*{Re.integer}', statements[0])
    if match is not None:
        statements_0 = match.groups()
        set_score = f"scoreboard players set $__private__.{statements_0[0]} __variable__ {statements_0[1]}"
    else:
        statements_0 = regex.match(
        f'let\s*{Re.var_nosigncap}\s*=\s*{Re.var}', statements[0]).groups()
        set_score = f"scoreboard players operation $__private__.{statements_0[0]} __variable__ = {statements_0[1]} __variable__"

    condition = Condition(statements[1].replace(
        f'${statements_0[0]}', f'$__private__.{statements_0[0]}'))
    content = groups[1].replace(
        f'${statements_0[0]}', f'$__private__.{statements_0[0]}')
    statement = statements[2].replace(
        f"${statements_0[0]}", f"$__private__.{statements_0[0]}")

    count = datapack.get_pfc("for_loop")

    datapack.private_functions["for_loop"][count] = Function(datapack.process_function_content(
        f"{content}; {statement}; {condition.pre_commands}execute{condition} run function {datapack.namespace}:__private__/for_loop/{count};"))

    return f'{set_score}; {condition.pre_commands}execute{condition} run function {datapack.namespace}:__private__/for_loop/{count};'
