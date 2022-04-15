from collections import defaultdict
from typing import TYPE_CHECKING, Any, Iterable
from json import JSONEncoder, dumps
from .tokenizer import Token, Tokenizer
from .exception import JMCSyntaxWarning
from .log import Logger

if TYPE_CHECKING:
    from .lexer import Lexer

logger = Logger(__name__)


NEW_LINE = '\n'


class FunctionEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Function):
            return o.commands
        return super().default(o)


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

    def insert_extend(self, commands: list[str], index: int) -> None:
        self.commands[index:index] = self.__split(commands)

    def delete(self, index: int) -> None:
        del self.commands[index]

    @property
    def content(self) -> str:
        return '\n'.join(self.commands)

    @property
    def length(self) -> int:
        return len(self.commands)

    def __repr__(self) -> str:
        return f"Function({repr(self.commands)})"

    def __iter__(self) -> Iterable:
        return self.commands.__iter__()

    def __bool__(self):
        return bool(self.commands)

    def __split(self, strings: list[str]) -> list[str]:
        return [self.optimize(str_) for string in strings for str_ in string.split('\n') if str_]

    def optimize(self, string: str) -> str:
        if string.startswith('execute'):
            if string.startswith('execute run '):
                string = string[12:]  # len('execute run ') = 11
        return string


class DataPack:
    PRIVATE_NAME = '__private__'
    LOAD_NAME = '__load__'
    TICK_NAME = '__tick__'
    VAR_NAME = '__variable__'
    INT_NAME = '__int__'
    VARIABLE_SIGN = '$'

    def __init__(self, namespace: str, lexer: "Lexer") -> None:
        logger.debug("Initializing Datapack")
        self.ints: set[int] = set()
        self.functions: dict[str, Function] = dict()
        self.load_function: list[list[Token]] = []
        self.jsons: dict[str, dict[str, Any]] = defaultdict(dict)
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

        self.used_command: set[str] = set()

        self.lexer = lexer

    def add_objective(self, objective: str, criteria: str = 'dummy') -> None:
        if objective in self.__scoreboards and self.__scoreboards[objective] != criteria:
            raise ValueError(
                f"Conflict on adding scoreboard, '{objective}' objective with '{self.__scoreboards[objective]}' criteria already exist.\nGot same objective with '{criteria}' criteria.")
        self.__scoreboards[objective] = criteria

    def get_count(self, name: str) -> str:
        count = self.private_function_count[name]
        self.private_function_count[name] += 1
        return str(count)

    def call_func(self, name: str, count: str) -> str:
        return f"function {self.namespace}:{self.PRIVATE_NAME}/{name}/{count}"

    def add_private_json(self, json_type: str, name: str, json: dict[str, Any]) -> None:
        self.jsons[f"{json_type}/{self.PRIVATE_NAME}/{name}"] = json

    def add_private_function(self, name: str, token: Token, tokenizer: Tokenizer) -> str:
        if token.string == '{}':
            raise JMCSyntaxWarning("Empty function", token, tokenizer)

        commands = self.parse_function_token(token, tokenizer)
        if len(commands) == 1 and NEW_LINE not in commands[0]:
            return commands[0]
        else:
            count = self.get_count(name)
            self.private_functions[name][count] = Function(commands)
            return self.call_func(name, count)

    def add_custom_private_function(self, name: str, token: Token, tokenizer: Tokenizer, count: str, precommands: list[str] = None, postcommands: list[str] = None) -> str:
        if precommands is None:
            precommands = []
        if postcommands is None:
            postcommands = []

        commands = [*precommands,
                    *self.parse_function_token(token, tokenizer),
                    *postcommands]
        self.private_functions[name][count] = Function(commands)
        return self.call_func(name, count)

    def add_raw_private_function(self, name: str, commands: list[str], count: str = None) -> str:
        if count is None:
            count = self.get_count(name)
        self.private_functions[name][count] = Function(commands)
        return self.call_func(name, count)

    def parse_function_token(self, token: Token, tokenizer: Tokenizer) -> list[str]:
        """Parse a curly bracket token into a list of string"""
        return self.lexer.parse_func_content(token.string[1:-1], tokenizer.file_path, token.line, token.col+1, tokenizer.file_string)

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
                self.functions[f"{self.PRIVATE_NAME}/{name}/{path}"] = func

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
    
    objectives = {dumps(self.__scoreboards, indent=2)}
    ints = {self.ints!r}
    functions = {dumps(self.functions, indent=2, cls=FunctionEncoder)}
    jsons = {dumps(self.jsons, indent=2)}
    private_functions = {dumps(self.private_functions, indent=2, cls=FunctionEncoder)}
    loads = {dumps(self.loads, indent=2)}
    tick = {dumps(self.ticks, indent=2)}

)"""

# {dumps({key:list(value) for key, value in self.functions.items()}, indent=2)}
