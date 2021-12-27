import logging
import re

from . import Logger, PackGlobal

logger = Logger(__name__, logging.INFO)


def clean_whitespace(string: str) -> str:
    """Replace whitespaces with space and return it"""
    logger.info("Cleaning whitespace")
    return re.sub(r"\s+", " ", string + ' ')


def custom_syntax(string: str, pack_global: PackGlobal) -> str:
    """Replace jmc syntax with mcfunction and return it"""
    def capture_var_assign(match: re.Match) -> str:
        pack_global.scoreboards.add('variable')
        groups = match.groups()
        rv = f'scoreboard players set {groups[0]} variable {int(groups[1])}'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = ([-+]?[0-9]+)', capture_var_assign, string)

    def capture_var_increment(match: re.Match) -> str:
        pack_global.scoreboards.add('variable')
        groups = match.groups()
        pack_global.ints.add(int(groups[2]))
        rv = f'scoreboard players operation {groups[0]} variable {groups[1]}= {groups[2]} INT'
        logger.debug(f"Custom Syntax: {rv}")
        return rv
    string = re.sub(r'(\$\w+) ([+\-\*/%])= ([-+]?[0-9]+)',
                    capture_var_increment, string)

    return string
