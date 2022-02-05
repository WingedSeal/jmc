import regex
import re

from ..utils import split, BracketRegex, Re, syntax_swap
from ..log import Logger

logger = Logger(__name__)

PARENTHESIS_REGEX = f"^{BracketRegex().match_bracket('()', 1)}$"


class Condition:
    def __init__(self, string: str, precommands: list[str] = None) -> None:
        if precommands is None:
            self._precommands: list[str] = []
        else:
            self._precommands = precommands

        string = string.strip()
        if regex.match(PARENTHESIS_REGEX, string) is not None:
            string = string[1:-1]
        self.condition = string

        or_conditions = split(self.condition, r'\|\|')
        if len(or_conditions) > 1:
            for or_condition in or_conditions:
                new_condition = Condition(or_condition)
                self._precommands += new_condition._precommands
                self._precommands.append(
                    f'execute{new_condition.condition} run scoreboards players set __logic__ __variable__ 1;')
            self.condition = ' if score __logic__ __variable__  matches 1'
            return

        and_conditions = split(self.condition, r'&&')
        if len(and_conditions) > 1:
            self.condition = ''
            for and_condition in and_conditions:
                new_condition = Condition(and_condition)
                self._precommands += new_condition._precommands
                self.condition += new_condition.condition
            return

        not_condition = re.match(r'!\s*(.+)', string)
        if not_condition is not None:
            print(not_condition.groups())
            not_condition = not_condition.groups()[0]
            new_condition = Condition(not_condition)
            self._precommands += new_condition._precommands
            # self._precommands.append(
            #     f'execute{new_condition.condition} run scoreboards players set __logic__ __variable__ 2;')
            # self.condition = ' unless score __logic__ __variable__  matches 2'
            self.condition = " ".join({"if": "unless", "unless": "if"}.get(
                substring, substring) for substring in new_condition.condition.split())
            self.condition = new_condition.condition.replace(
                'if', "%^tw'tC;UA#mn?2$")
            self.condition = syntax_swap(
                new_condition.condition, 'if', 'unless')
            return

        # TODO: Handle custom syntax

        self.condition = f' if {condition(self.condition)}'

    @property
    def pre_commands(self) -> str:
        if len(self._precommands) > 0:
            self._precommands.insert(
                0, 'scoreboards players set __logic__ __variable__ 0;')
            return "".join(self._precommands)
        else:
            return ""

    def __repr__(self) -> str:
        return self.condition


def condition(string: str) -> str:
    """Turn variable conditions into `if score`"""
    def equal_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches {groups[1]}'
    string, success = re.subn(
        f'^{Re.var}\s*(?:==|=)\s*{Re.integer}$', equal_int, string)
    if success:
        return string

    def equal_range(match: re.Match) -> str:
        groups = match.groups()
        start = groups[1] if groups[1] is not None else ''
        end = groups[2] if groups[2] is not None else ''
        return f'score {groups[0]} __variable__ matches {start}..{end}'
    string, success = re.subn(
        f'^{Re.var}\s*(?:==|=)\s*{Re.match_range}$', equal_range, string)
    if success:
        return string

    def more_than_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches {int(groups[1])+1}..'
    string, success = re.subn(
        f'^{Re.var}\s*>\s*{Re.integer}$', more_than_int, string)
    if success:
        return string

    def less_than_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches ..{int(groups[1])-1}'
    string, success = re.subn(
        f'^{Re.var}\s*<\s*{Re.integer}$', less_than_int, string)
    if success:
        return string

    def more_than_eq_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches {groups[1]}..'
    string, success = re.subn(
        f'^{Re.var}\s*>=\s*{Re.integer}$', more_than_eq_int, string)
    if success:
        return string

    def less_than_eq_int(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ matches ..{groups[1]}'
    string, success = re.subn(
        f'^{Re.var}\s*<=\s*{Re.integer}$', less_than_eq_int, string)
    if success:
        return string

    def operation_var(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ {groups[1]} {groups[2]} __variable__'
    string, success = re.subn(
        f'^{Re.var}\s*(<|<=|=|>=|>)\s*{Re.var}$', operation_var, string)
    if success:
        return string

    def equal_var(match: re.Match) -> str:
        groups = match.groups()
        return f'score {groups[0]} __variable__ = {groups[1]} __variable__'
    string, success = re.subn(
        f'^{Re.var}\s*==\s*{Re.var}$', equal_var, string)
    if success:
        return string

    return string
