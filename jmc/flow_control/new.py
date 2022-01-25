import regex
import json
import re
from typing import TYPE_CHECKING

from ..config import JMCSyntaxError
from ..utils import BracketRegex
from .. import Logger

if TYPE_CHECKING:
    from ..datapack import DataPack

logger = Logger(__name__)

bracket_regex = BracketRegex()
NEW_REGEX = r'^new\s*([\w\._]+)\s*'+ bracket_regex.match_bracket('()', 2) + r'\s*' + bracket_regex.match_bracket('{}', 3)  # noqa

def capture_new(self: "DataPack", line: str, prefix: str = ''):
    logger.debug("Searching for New")
    line = line.strip()
    logger.debug(line)

    def new_found(match: re.Match):
        new_type, new_name, new_content = bracket_regex.compile(match.groups())
        logger.debug(f"New found - {new_type} - {prefix}{new_name}")
        try:
            new_dict = json.loads(f'{{{new_content}}}')
        except json.decoder.JSONDecodeError as error:
            raise JMCSyntaxError(f'Malformed JSON, In {new_type}/{prefix}{new_name}\n{error}')
        self.news[
            new_type.replace('.', '/')][f'{prefix}{new_name}'.lower().replace(
            '.', '/')] = new_dict
        return ""
    line, success = regex.subn(NEW_REGEX, new_found, line, count=1)

    if success:
        logger.debug(f"Recursing capture_new()")
        line = self.capture_new(line, prefix)
    else:
        logger.debug("No Function found")

    line = self.capture_class(line, prefix)
    return line