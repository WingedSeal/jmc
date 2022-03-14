from enum import Enum

from .exclude_execute import EXCLUDE_EXECUTE_COMMANDS
from .jmc import JMC_COMMANDS
from .load_once import LOAD_ONCE_COMMANDS, used_command
from .flow_control import FLOW_CONTROL_COMMANDS


def clean_up_paren(string: str) -> str:
    new_string = ""
    is_string = False
    is_escaped = False
    quote = None
    for char in string:
        if is_string:
            if is_escaped:
                is_escaped = False
            else:
                if char == "\\":
                    is_escaped = True
                elif char == quote:
                    is_string = False
            new_string += char

        else:
            if char in ['\t', ' ', '\n']:
                continue
            elif char in ['"', "'"]:
                quote = char
                is_string = True
            new_string += char

    return new_string
