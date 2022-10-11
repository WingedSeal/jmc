from enum import Enum, auto
from typing import Callable

from .utils import ArgType, find_scoreboard_player_type, verify_args, Arg
from ..datapack import DataPack
from ..exception import JMCMissingValueError
from ..tokenizer import Token, Tokenizer


class FuncType(Enum):
    bool_function = auto()
    execute_excluded = auto()
    jmc_command = auto()
    load_once = auto()
    load_only = auto()
    variable_operation = auto()


class JMCFunction:
    """
    Base function for all custom JMC function

    :param token: paren_round token containing arguments
    :param datapack: Datapack object
    :param tokenizer: Tokenizer
    :param is_execute: Whether the function is in execute command (Can be None if not used), defaults to None
    :param var: For containing minecraft variable (Can be None if not used), defaults to None

    :raises NotImplementedError: If JMCFunction isn't used with decorator
    :raises NotImplementedError: Missing func_type
    :raises JMCValueError: Missing required positional argument
    :raises NotImplementedError: Call function not implemented
    """
    _decorated = False
    """A private attribute that will be changed by a decorator to check for missing decorator"""
    arg_type: dict[str, ArgType]
    func_type: FuncType
    name: str
    call_string: str
    defaults: dict[str, str]
    _ignore: set[str]

    def __new__(cls, *args, **kwargs):
        if cls is JMCFunction:
            raise TypeError(f"Only children of '{cls.__name__}' may be instantiated")
        return super().__new__(cls)

    def __init__(self, token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: bool|None = None, var: str = None) -> None:
        self.token = token
        self.datapack = datapack
        self.tokenizer = tokenizer
        self.is_execute = is_execute
        self.var = var
        if not self._decorated:
            raise NotImplementedError("Missing decorator")
        if self.func_type is None:
            raise NotImplementedError("Missing func_type")

        self.__args_Args = verify_args(self.arg_type,
                                     self.call_string, token, tokenizer)
        self.args: dict[str, str] = {}
        self.raw_args: dict[str, Arg] = {}

        for key, arg in self.__args_Args.items():
            if arg is None:
                if key not in self.defaults:
                    raise JMCMissingValueError(key, token, tokenizer)
                self.args[key] = self.defaults[key]
            else:
                self.raw_args[key] = arg
                if key in self._ignore:
                    pass
                elif arg.arg_type == ArgType._func_call:
                    self.args[key] = f"function {datapack.namespace}:{arg.token.string.lower().replace('.', '/')}"
                elif arg.arg_type == ArgType.arrow_func:
                    self.args[key] = '\n'.join(
                        datapack.parse_function_token(arg.token, tokenizer))
                elif arg.arg_type == ArgType.integer:
                    self.args[key] = str(find_scoreboard_player_type(
                        arg.token, tokenizer).value)
                elif arg.arg_type in {ArgType.scoreboard_player, ArgType.scoreboard}:
                    scoreboard_player = find_scoreboard_player_type(
                        arg.token, tokenizer)
                    if isinstance(scoreboard_player.value, int):
                        raise ValueError(
                            "scoreboard_player.value is int for minecraft scorboard")
                    self.args[key] = f"{scoreboard_player.value[1]} {scoreboard_player.value[0]}"
                else:
                    self.args[key] = arg.token.string

        self.__post__init__()

    def __post__init__(self) -> None:
        """
        This function will be called after initiation of the object
        """
        pass

    def call(self) -> str:
        """
        This function will be called when user call matching JMC custom function 

        :raises NotImplementedError: When the subclass's call method is not implemented
        :return: Minecraft command as string
        """
        raise NotImplementedError("Call function not implemented")

    def call_bool(self) -> tuple[str, bool]:
        """
        This function will be called when user call matching JMC *boolean* function 

        :raises NotImplementedError: When the subclass's call method is not implemented
        :return: Tuple of Minecraft command as string and IF/UNLESS(boolean)
        """
        raise NotImplementedError("Call(Bool) function not implemented")

    @classmethod
    def _get(cls, func_type: FuncType) -> dict[str, type["JMCFunction"]]:
        """
        Get dictionary of funtion name and a class matching function type

        :param func_type: Function type to search for
        :return: Dictionary of jmcfunction name and jmcfunction class
        """
        commands = {}
        for subcls in cls.__subclasses__():
            if subcls.func_type == func_type:
                commands[subcls.call_string] = subcls
        return commands


def func_property(func_type: FuncType, call_string: str, name: str, arg_type: dict[str, ArgType], defaults: dict[str, str] = {}, ignore: set[str] = set()) -> Callable[[type[JMCFunction]], type[JMCFunction]]:
    """
    Decorator factory for setting property of custom JMC function

    :param func_type: Type of custom function
    :param call_string: String for user to call the function
    :param name: Name for further usage
    :param arg_type: Dictionary of arguments(string) and type of the argument(ArgType)
    :param defaults: Dictionary of arguments(string and default of it(string or integer)), defaults to {}
    :param ignore: Set of arguments(string) for parser to ignore and don't parse(For futher custom parsing), defaults to set()
    :return: A decorator
    """
    def decorator(cls: type[JMCFunction]) -> type[JMCFunction]:
        """
        A decorator to set the class's attributes for setting JMC function's properties

        :param cls: A subclass of JMCFunction
        :return: Same class that was passed in  
        """
        cls.func_type = func_type
        cls.call_string = call_string
        cls.arg_type = arg_type
        cls.defaults = defaults
        cls._ignore = ignore
        cls.name = name

        cls._decorated = True
        return cls
    return decorator
