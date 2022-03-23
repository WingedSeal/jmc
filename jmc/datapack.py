from collections import defaultdict
from turtle import pos
from typing import TYPE_CHECKING, Iterable
from json import dumps
from .tokenizer import Token, Tokenizer
from .exception import JMCSyntaxWarning
from .log import Logger

if TYPE_CHECKING:
    from .lexer import Lexer

logger = Logger(__name__)


NEW_LINE = '\n'


class Function:
    commands: list[str]

    def __init__(self, commands: list[str] = None) -> None:
        if commands is None:
            self.commands = []
        else:
            self.commands = self.__split(commands)

    def add_empty_line(self) -> None:
        self.commands.append('')

    def append(self, command: str) -> None:
        self.commands.extend(self.__split([command]))

    def extend(self, commands: list[str]) -> None:
        self.commands.extend(self.__split(commands))

    def __repr__(self) -> str:
        return f"Function({repr(self.commands)})"

    def __iter__(self) -> Iterable:
        return self.commands.__iter__()

    def __split(self, strings: list[str]) -> list[str]:
        return [str_ for string in strings for str_ in string.split('\n') if str_]


class DataPack:
    PRIVATE_NAME = '__private__'
    LOAD_NAME = '__load__'
    TICK_NAME = '__tick__'

    def __init__(self, namespace: str, lexer: "Lexer") -> None:
        logger.debug("Initializing Datapack")
        self.ints: set[int] = set()
        self.functions: dict[str, Function] = dict()
        self.load_function: list[list[Token]] = []
        self.jsons: dict[str, dict[str, dict]] = defaultdict(dict)
        self.private_functions: dict[str,
                                     dict[str, Function]] = defaultdict(dict)
        self.private_function_count: dict[str, int] = defaultdict(int)

        self.loads: list[str] = []
        self.ticks: list[str] = []
        self.namespace = namespace

        self.lexer = lexer

    def get_count(self, name: str) -> int:
        count = self.private_function_count[name][count]
        self.private_function_count[name] += 1
        return count

    def add_private_function(self, name: str, token: Token, tokenizer: Tokenizer) -> str:
        if token.string == '{}':
            raise JMCSyntaxWarning(
                f"In {tokenizer.file_path}\nEmpty function at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col+1]} <-"
            )
        commands = self.lexer.parse_func_content(
            token.string[1:-1], tokenizer.file_path, line=token.line, col=token.col, file_string=tokenizer.file_string)
        if len(commands) == 1 and NEW_LINE not in commands[0]:
            return commands[0]
        else:
            count = self.get_count()
            self.private_functions[name][count] = Function(commands)
            return f"function {self.PRIVATE_NAME}/{name}/{count}"

    def add_custom_private_function(self, name: str, token: Token, tokenizer: Tokenizer, count: int, precommands: list[str] = None, postcommands: list[str] = None) -> str:
        if precommands is None and postcommands is None:
            raise ValueError(
                "add_custom_private_function is called without pre/post command")
        if precommands is None:
            precommands = []
        if postcommands is None:
            postcommands = []

        commands = [*precommands,
                    *self.lexer.parse_func_content(
                        token.string[1:-1], tokenizer.file_path, line=token.line, col=token.col, file_string=tokenizer.file_string),
                    *postcommands]
        self.private_functions[name][count] = Function(commands)
        self.private_function_count[name] += 1
        return f"function {self.PRIVATE_NAME}/{name}/{count}"

    def add_raw_private_function(self, name: str, commands: list[str]) -> str:
        count = self.get_count()
        self.private_functions[name][count] = Function(commands)
        return f"function {self.PRIVATE_NAME}/{name}/{count}"

    def __repr__(self) -> str:
        return f"""DataPack(
    PRIVATE_STR = {self.PRIVATE_NAME},
    LOAD_NAME = {self.LOAD_NAME},
    TICK_NAME = {self.TICK_NAME},
    
    ints = {self.ints!r}
    function = 
{dumps(self.functions, indent=2)}
    jsons =
{dumps(self.jsons, indent=2)}
    private_functions = 
{dumps(self.private_functions, indent=2)}
)"""
