from cProfile import run
from pathlib import Path


from .exception import JMCFileNotFoundError, JMCSyntaxException
from .vanilla_command import COMMANDS
from .tokenizer import Tokenizer, Token, TokenType

FIRST_ARGUMENTS = [
    *COMMANDS,
    "TEST"
]
"""All vanilla commands and JMC custom syntax 

`if` is excluded from the list since it can be used in execute"""
NEW_LINE = '\n'


class Lexer:
    def __init__(self, config: dict[str, str]) -> None:
        self.config = config
        self.parse_file(Path(self.config["target"]))

    def parse_file(self, file_path: Path) -> None:
        try:
            with file_path.open('r') as file:
                raw_string = file.read()
        except FileNotFoundError:
            raise JMCFileNotFoundError(
                f"JMC file not found: {file_path.resolve().as_posix()}")
        tokenizer = Tokenizer(raw_string, file_path.name)

        for line_count, command in enumerate(tokenizer.programs):
            is_execute = (command[0].string == 'execute')
            for key_pos, token in enumerate(command):
                if (
                    token.token_type == TokenType.keyword and
                    token.string in FIRST_ARGUMENTS and
                    key_pos != 0 and
                    command[key_pos-1].string != 'run'
                ):
                    col = command[key_pos-1].col+command[key_pos-1].length
                    raise JMCSyntaxException(
                        f"In {tokenizer.file_name}\nKeyword({token.string}) at line {token.line} col {token.col} is regonized as a command.\nExpected semicolon(;) at line {command[key_pos-1].line} col {col}\n{tokenizer.raw_string.split(NEW_LINE)[command[key_pos-1].line-1][:col-1]} <-"
                    )
