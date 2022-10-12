from collections import defaultdict
from typing import TYPE_CHECKING, Any, Iterable
from json import JSONEncoder, dumps
from .tokenizer import Token, Tokenizer
from .exception import JMCSyntaxWarning
from .log import Logger

if TYPE_CHECKING:
    from .lexer import Lexer
    from .header import Header

logger = Logger(__name__)


NEW_LINE = '\n'


class FunctionEncoder(JSONEncoder):
    """
    Custom minecraft function encoder for json.dump
    """
    def default(self, o):
        if isinstance(o, Function):
            return o.commands
        return super().default(o)


class Function:
    """
    A class representation for a minecraft function (.mcfunction)

    :param commands: List of minecraft commands(string), defaults to empty list
    """
    __slots__ = 'commands'
    commands: list[str]

    def __init__(self, commands: list[str] = None) -> None:
        if commands is None:
            self.commands = []
        else:
            self.commands = self.__split(commands)

    def add_empty_line(self) -> None:
        """
        Add empty line at the end of the function
        """
        self.commands.append('')

    def append(self, command: str) -> None:
        """
        Append 1 or more command in form of a single string

        :param command: 1 or more line of minecraft command string
        """
        self.commands.extend(self.__split([command]))

    def extend(self, commands: list[str]) -> None:
        """
        Append multiple minecraft commands

        :param commands: List of minecraft commands(strings), each string can have multiple lines 
        """
        self.commands.extend(self.__split(commands))

    def insert_extend(self, commands: list[str], index: int) -> None:
        """
        Append multiple minecraft commands to a certine line of function

        :param commands:  List of minecraft commands(strings), each string can have multiple lines 
        :param index: Line/Position of the function to insert to
        """
        self.commands[index:index] = self.__split(commands)

    def delete(self, index: int) -> None:
        """
        Delete a command

        :param index: Line/Position of the function to delete
        """
        del self.commands[index]

    @property
    def content(self) -> str:
        """
        Content of the function in 1 string

        :return: Commands of the function in form of a single string
        """
        return '\n'.join(self.commands)

    @property
    def length(self) -> int:
        """
        Amount of lines in the function (including empty lines)

        :return: Length of commands attribute
        """
        return len(self.commands)

    def __repr__(self) -> str:
        return f"Function({repr(self.commands)})"

    def __iter__(self) -> Iterable:
        return self.commands.__iter__()

    def __bool__(self):
        return bool(self.commands)

    def __split(self, strings: list[str]) -> list[str]:
        """
        Loop through every line in each string of command(s) and make a new list with every element having only 1 line of command while optimizing every command

        :param strings: minecraft commands(strings),each string can have multiple lines 
        :return: minecraft commands(strings),each string can have only a single line
        """
        return [self.optimize(str_) for string in strings for str_ in string.split('\n') if str_]

    def optimize(self, string: str) -> str:
        """
        Optimize minecraft command by remove redundancy

        :param string: A minecraft command
        :return: An optimized minecraft command

        .. todo:: Finish optimization
        """
        if string.startswith('execute'):
            if string.startswith('execute run '):
                string = string[12:]  # len('execute run ') = 11
        return string
class DataPack:
    """
    A class representation for entire minecraft datapack

    :param namespace: Datapack's namespace
    :param lexer: Lexer object
    """
    __slot__ = ('PRIVATE_NAME', 'LOAD_NAME', 'TICK_NAME',
                'VAR_NAME', 'INT_NAME', 'VARIABLE_SIGN',
                'HEADER_DATA', '_tick_json', 'ints',
                'functions', 'load_function', 'jsons',
                'private_functions', 'private_function_count',
                '__scoreboards', 'loads', 'ticks', 'namespace',
                'used_command', 'lexer')
    PRIVATE_NAME = '__private__'
    LOAD_NAME = '__load__'
    TICK_NAME = '__tick__'
    VAR_NAME = '__variable__'
    INT_NAME = '__int__'
    VARIABLE_SIGN = '$'
    HEADER_DATA: "Header|None" = None
    """Data read from header file(s)"""

    _tick_json = None


    def __init__(self, namespace: str, lexer: "Lexer") -> None:
        logger.debug("Initializing Datapack")
        self.ints: set[int] = set()
        """Set of integers going to be used in scoreboard"""
        self.functions: dict[str, Function] = {}
        """Dictionary of function name and a Function object"""
        self.load_function: list[list[Token]] = []
        """List of commands(list of tokens) in load function"""
        self.jsons: dict[str, dict[str, Any]] = defaultdict(dict)
        """Dictionary of json name and a dictionary(jsobject)"""
        self.private_functions: dict[str,
                                     dict[str, Function]] = defaultdict(dict)
        """Dictionary of function's group name and (Dictionary of function name and a Function object)"""
        self.private_function_count: dict[str, int] = defaultdict(int)
        """Current count of how many private functions there are in each group name"""
        self.__scoreboards: dict[str, str] = {
            self.VAR_NAME: 'dummy',
            self.INT_NAME: 'dummy'
        }
        """Minecraft scoreboards that are going to be created"""

        self.loads: list[str] = []
        """Output list of commands for load"""
        self.ticks: list[str] = []
        """Output list of commands for tick"""
        self.namespace = namespace
        """Datapack's namespace"""

        self.used_command: set[str] = set()
        """Used JMC command that's for one time call only"""

        self.lexer = lexer
        """Lexer object"""

    def add_objective(self, objective: str, criteria: str = 'dummy') -> None:
        """
        Add minecraft scoreboard objective

        :param objective: Name of scoreboard
        :param criteria: Criteria of scoreboard, defaults to 'dummy'
        :raises ValueError: If scoreboard already exists
        """
        if objective in self.__scoreboards and self.__scoreboards[objective] != criteria:
            raise ValueError(
                f"Conflict on adding scoreboard, '{objective}' objective with '{self.__scoreboards[objective]}' criteria already exist.\nGot same objective with '{criteria}' criteria.")
        self.__scoreboards[objective] = criteria

    def get_count(self, name: str) -> str:
        """
        Get count as a string from private function's group

        :param name: Name of the function group
        :return: Count as a string
        """
        count = self.private_function_count[name]
        self.private_function_count[name] += 1
        return str(count)

    def call_func(self, name: str, count: str) -> str:
        """
        Get command string for calling minecraft private function

        :param name: Name of the private function group
        :param count: Name of the function (usually as count)
        :return: String for calling minecraft function
        """
        return f"function {self.namespace}:{self.PRIVATE_NAME}/{name}/{count}"

    def add_private_json(self, json_type: str, name: str, json: dict[str, Any]) -> None:
        """
        Add new private json to datapack

        :param json_type: Minecraft json type, for example: tags/functions
        :param name: Name of the private json
        :param json: Dictionary object
        """
        self.jsons[f"{json_type}/{self.PRIVATE_NAME}/{name}"] = json

    def add_private_function(self, name: str, token: Token, tokenizer: Tokenizer) -> str:
        """
        Add private function for user (arrow function)

        :param name: Private function's group name
        :param token: paren_curly token
        :param tokenizer: token's tokenizer
        :raises JMCSyntaxWarning: If the string in curly bracket is empty
        :return: Minecraft function call string
        """
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
        """
        Wrap custom commands around user's commands

        :param name: Private function's group name
        :param token: paren_curly token
        :param tokenizer: token's tokenizer
        :param count: Name of the function (usually as count)
        :param precommands: Commands before user's commands
        :param postcommands: Commands after user's commands
        :return: Minecraft function call string
        """
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
        """
        Add private function for JMC

        :param name: Name of the private function's group
        :param commands: List of commands(string)
        :param count: Name of the function (usually as count), defaults to current count + 1
        :return: Minecraft function call string
        """
        if count is None:
            count = self.get_count(name)
        self.private_functions[name][count] = Function(commands)
        return self.call_func(name, count)

    def parse_function_token(self, token: Token, tokenizer: Tokenizer) -> list[str]:
        """
        "Parse a paren_curly token into a list of commands(string)

        :param token: paren_curly token
        :param tokenizer: token's tokenizer
        :return: List of minecraft commands(string)
        """
        return self.lexer.parse_func_content(token.string[1:-1], tokenizer.file_path, token.line, token.col+1, tokenizer.file_string)

    def build(self) -> None:
        """
        Finializing DataPack for building (NO file writing)
        """
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

        self.private_functions = {}
        self.loads = []
        self.ticks = []

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