import regex
import re
from typing import TYPE_CHECKING
from ast import  literal_eval
from math import floor, ceil

from ..utils import BracketRegex, split, Re
from ..config import JMCSyntaxError
from .function_ import Function
from .. import Logger


if TYPE_CHECKING:
    from ..datapack import DataPack

logger = Logger(__name__)

bracket_regex = BracketRegex()
SWITCH_CASE_REGEX = r'^switch\s*\(' + Re.var + r'\)\s*' + bracket_regex.match_bracket('{}', 2)  # noqa

def capture_switch_case(self: "DataPack", line: str) -> tuple[str, bool]:

    line = line.strip()

    def switch_case_found(match: re.Match):
        logger.debug("Switch Case found")
        groups = bracket_regex.compile(match.groups())
        return handle_switch_case(self, groups)
    line, success = regex.subn(SWITCH_CASE_REGEX, switch_case_found, line, count=1)

    return line, success



def handle_switch_case(datapack: "DataPack", groups: tuple[str]) -> str:
    
    var = groups[0]
    cases = split(groups[1], r'case\s*[0-9]+\s*:')
    cases = [case[:-6] if case.endswith("break;") else case for case in cases][1:]

    def binary(min_: int, max_: int, count: int) -> None:
        if max_ < min_:
            raise JMCSyntaxError("Switch Case error: Do not use Hardcode.repeat() with Switch Case.")
        if max_ == min_:
            datapack.private_functions["switch_case"][count] = Function(datapack.process_function_content(cases[min_-1]))
        else:
            count_less = datapack.get_pfc("switch_case")
            count_more = datapack.get_pfc("switch_case")

            half2 = min_+(max_-min_+1)//2
            half1 = half2-1

            match_less = f"{min_}..{half1}" if min_!=half1 else min_
            match_more = f"{half2}..{max_}" if half2!=max_ else max_

            datapack.private_functions["switch_case"][count] = Function(datapack.process_function_content(
                f"""execute if score {var} __variable__ matches {match_less} run function {datapack.namespace}/__private__/switch_case/{count_less};
execute if score {var} __variable__ matches {match_more} run function {datapack.namespace}/__private__/switch_case/{count_more};"""
            ))

            binary(min_, half1, count_less)
            binary(half2, max_, count_more)

    count = datapack.get_pfc("switch_case")
    binary(1, len(cases), count)

    return f"function {datapack.namespace}/__private__/switch_case/{count};"

    