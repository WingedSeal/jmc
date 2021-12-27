import logging
import regex as re

from . import Logger, PackGlobal

logger = Logger(__name__, logging.INFO)


def clean_whitespace(string: str) -> str:
    """Replace whitespaces with space and return it"""
    logger.info("Cleaning whitespace")
    return re.sub(r"\s+", " ", string + ' ')


def custom_syntax(string: str, pack_global: PackGlobal) -> str:
    """Replace jmc syntax with mcfunction and return it"""
    def capture_var_assign(match: re.Match) -> str:
        """$<VARIABLE> = <INT>"""
        groups = match.groups()
        rv = f'scoreboard players set {groups[0]} __variable__ {int(groups[1])}'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = ([-+]?[0-9]+)', capture_var_assign, string)

    def capture_var_increment(match: re.Match) -> str:
        """$<VARIABLE> += <INT>, and others"""
        groups = match.groups()
        pack_global.ints.add(int(groups[2]))
        rv = f'scoreboard players operation {groups[0]} __variable__ {groups[1]}= {groups[2]} __int__'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+) ([+\-\*/%])= ([-+]?[0-9]+)',
                    capture_var_increment, string)

    def capture_var_equal(match: re.Match) -> str:
        """$<VARIABLE> = $<VARIABLE>"""
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ = {groups[1]}'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = (\$\w+)', capture_var_equal, string)

    def capture_var_equal(match: re.Match) -> str:
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ = {groups[1]}'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = (\$\w+)', capture_var_equal, string)

    def capture_var_increment_var(match: re.Match) -> str:
        """$<VARIABLE> += $<VARIABLE>, and others"""
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ {groups[1]}= {groups[2]} __variable__'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+) ([+\-\*/%])= (\$\w+)',
                    capture_var_increment_var, string)

    def capture_to_string(match: re.Match) -> str:
        """$<VARIABLE> += $<VARIABLE>, and others"""
        groups = match.groups()
        rv = f'{{"score":{{"name":"{groups[0]}","objective":"variable"}}{"," if groups[1] != "" else ""}{groups[1]}}}'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+)\.toString\(((?:[^)(]+|(?R))*+)\)',
                    capture_to_string, string)

    return string
