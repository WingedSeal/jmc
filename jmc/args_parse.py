import re
import regex

from .utils import split, BracketRegex
from . import Logger

    
logger = Logger(__name__)

class NoKeyExecption(BaseException):
    pass

def parse_value(string: str) -> str:
    """Check if value is a normal string or an arrow function

    Args:
        string (str): Value

    Returns:
        str: Value if it's normal string else Function Content
    """
    content, success = re.subn(r'^\(\s*\)\s*=>\s*{(.*)}$', r'\1', string)
    if not success:
        return string
    return content
    

def args_parse(string: str, defaults: dict[str, str]) -> dict:
    args = split(string)
    json = dict()
    keys = list(defaults.keys())
    for i, arg in enumerate(args):
        match = re.match(r'^([\w_]+)=(.*)$', arg)
        if match is not None:
            key, value = match.groups()
            if key not in defaults.keys():
                raise NoKeyExecption("Key does not exist")
            json[key] = parse_value(value)
        else:
            json[keys[i]] = parse_value(arg)
    defaults.update(json)
    return defaults


def parse_func_json(string: str) -> list[tuple[str,str]]:
    funcs = split(string[1:-1])
    json = dict()
    for func in funcs:
        if func == '':
            continue
        bracket_regex = BracketRegex()
        match: re.Match = regex.match(r'(\d+)\s*:\s*\(\s*\)\s*=>\s*' + bracket_regex.match_bracket('{}', 2), func)
        key, content = bracket_regex.compile(match.groups())
        json[key] = content
    return json.items()