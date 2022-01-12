import logging
import re
import regex

from . import Logger, PackGlobal

logger = Logger(__name__)


def clean_whitespace(string: str) -> str:
    """Replace whitespaces with space and return it"""
    logger.info("Cleaning whitespace")
    return re.sub(r"\s+", " ", string + ' ')


def clean_comments(string: str) -> str:
    """Delete everything that starts with # or // until the end of the line"""
    logger.info("Cleaning comments")
    return re.sub(r"#.*|\/\/.*", "", string)


def custom_syntax(string: str, pack_global: PackGlobal) -> str:
    """Replace jmc syntax with mcfunction and return it"""
    logger.info("Handling custom syntax")

    def capture_var_assign(match: re.Match) -> str:
        """$<VARIABLE> = <INT>"""
        groups = match.groups()
        rv = f'scoreboard players set {groups[0]} __variable__ {int(groups[1])}'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = ([-+]?[0-9]+)', capture_var_assign, string)

    def capture_var_increment(match: re.Match) -> str:
        """$<VARIABLE> += <INT>, and others"""
        groups = match.groups()
        pack_global.ints.add(int(groups[2]))
        rv = f'scoreboard players operation {groups[0]} __variable__ {groups[1]}= {groups[2]} __int__'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) ([+\-\*/%])= ([-+]?[0-9]+)',
                    capture_var_increment, string)

    def capture_var_equal(match: re.Match) -> str:
        """$<VARIABLE> = $<VARIABLE>"""
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ = {groups[1]}'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = (\$\w+)', capture_var_equal, string)

    def capture_var_equal(match: re.Match) -> str:
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ = {groups[1]}'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) = (\$\w+)', capture_var_equal, string)

    def capture_var_increment_var(match: re.Match) -> str:
        """$<VARIABLE> += $<VARIABLE>, and others"""
        groups = match.groups()
        rv = f'scoreboard players operation {groups[0]} __variable__ {groups[1]}= {groups[2]} __variable__'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = re.sub(r'(\$\w+) ([+\-\*/%])= (\$\w+)',
                    capture_var_increment_var, string)

    def capture_to_string(match: re.Match) -> str:
        """$<VARIABLE> += $<VARIABLE>, and others"""
        groups = match.groups()
        if groups[1] != "":
            styles = groups[1].replace(' ', '').split(',')
            for i, style in enumerate(styles):
                style = style.split('=')
                styles[i] = f'"{style[0]}":{style[1]}'
            styles = ', '.join(['']+styles)
        else:
            styles = ''
        styles: str
        rv = f'{{"score":{{"name":"{groups[0]}","objective":"variable"}}{styles}}}'
        logger.debug(f"Custom Syntax:\nfrom: {match.group()}\nto: {rv}")
        return rv
    string = regex.sub(r'(\$\w+)\.toString\(((?:[^)(]+|(?R))*+)\)',
                       capture_to_string, string)

    return string


def replace_function_call(command_text: str, pack_global: PackGlobal) -> str:
    """Replace `<functionName>()` with `function <namespace>:<functionName>` in command"""
    def mcfunction(match: re.Match) -> str:
        return f'function {pack_global.namespace}:{match.groups()[0].replace(".", "/").lower()}'
    command_text = re.sub(
        r'([\w\.]+)\(\)', mcfunction, command_text)
    return command_text
