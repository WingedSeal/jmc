from ..tokenizer import Token
from .exclude_execute import EXCLUDE_EXECUTE_COMMANDS
from .jmc import JMC_COMMANDS
from .load_once import LOAD_ONCE_COMMANDS, used_command


def clean_up_paren(string: str) -> str:
    # TODO: Implement better cleaning
    return string.replace('\n', '')
