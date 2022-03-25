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


class Function(list):
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

    def insert_extend(self, commands: list[str], index: int) -> None:
        self.commands[index:index] = self.__split(commands)

    @property
    def content(self) -> str:
        return '\n'.join(self.commands)

    @property
    def length(self) -> str:
        return len(self.commands)

    def __repr__(self) -> str:
        return f"Function({repr(self.commands)})"

    def __iter__(self) -> Iterable:
        return self.commands.__iter__()

    def __bool__(self):
        return bool(self.commands)

    def __split(self, strings: list[str]) -> list[str]:
        return [str_ for string in strings for str_ in string.split('\n') if str_]


class DataPack:
    PRIVATE_NAME = '__private__'
    LOAD_NAME = '__load__'
    TICK_NAME = '__tick__'
    VAR_NAME = '__variable__'
    INT_NAME = '__int__'

    def __init__(self, namespace: str, lexer: "Lexer") -> None:
        logger.debug("Initializing Datapack")
        self.ints: set[int] = set()
        self.functions: dict[str, Function] = dict()
        self.load_function: list[list[Token]] = []
        self.jsons: dict[str, dict[str, dict]] = defaultdict(dict)
        self.private_functions: dict[str,
                                     dict[str, Function]] = defaultdict(dict)
        self.private_function_count: dict[str, int] = defaultdict(int)
        self.__scoreboards: dict[str, str] = {
            self.VAR_NAME: 'dummy',
            self.INT_NAME: 'dummy'
        }

        self.loads: list[str] = []
        self.ticks: list[str] = []
        self.namespace = namespace

        self.lexer = lexer

    def add_objective(self, objective: str, criteria: str = 'dummy') -> None:
        if objective in self.__scoreboards and self.__scoreboards[objective] != criteria:
            raise ValueError(
                f"Conflict on adding scoreboard, '{objective}' objective with '{self.__scoreboards[objective]}' criteria already exist.\nGot same objective with '{criteria}' criteria.")
        self.__scoreboards[objective] = criteria

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

    def build(self) -> None:
        logger.debug("Finializing DataPack")
        self.loads[0:0] = [
            *[f"scoreboard objectives add {objective} {criteria}" for objective,
                criteria in self.__scoreboards.items()],
            *[f"scoreboard players set {n} {self.INT_NAME} {n}" for n in self.ints],
        ]
        if self.loads:
            self.functions[self.LOAD_NAME].insert_extend(self.loads, 0)
        if self.ticks:
            if self.TICK_NAME in self.functions:
                self.functions[self.TICK_NAME].insert_extend(self.ticks, 0)
            else:
                self.functions[self.TICK_NAME] = Function(self.ticks)
        for name, functions in self.private_functions.items():
            for path, func in functions.items():
                self.functions[f"{name}/{path}"] = func

        self.private_functions = None
        self.loads = None
        self.ticks = None

    def __repr__(self) -> str:
        return f"""DataPack(
    PRIVATE_NAME = {self.PRIVATE_NAME},
    LOAD_NAME = {self.LOAD_NAME},
    TICK_NAME = {self.TICK_NAME},
    VAR_NAME = {self.VAR_NAME},
    INT_NAME = {self.INT_NAME}
    
    ints = {self.ints!r}
    function = 
{dumps({key:list(value) for key, value in self.functions.items()}, indent=2)}
    jsons =
{dumps(self.jsons, indent=2)}
    private_functions = 
{dumps({key:list(value) for key, value in self.private_functions.items()}, indent=2)}
)"""
