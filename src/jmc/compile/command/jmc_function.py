from collections import defaultdict
from enum import Enum, auto
from json import JSONDecodeError, loads
from typing import Any, Callable

from jmc.compile.utils import convention_jmc_to_mc

from .utils import ArgType, find_scoreboard_player_type, verify_args, Arg
from ..datapack import DataPack, Function
from ..exception import JMCDecodeJSONError, JMCMissingValueError
from ..tokenizer import Token, Tokenizer


class FuncType(Enum):
    BOOL_FUNCTION = auto()
    """Returns a part of `/execute if` command"""
    EXECUTE_EXCLUDED = auto()
    """Cannot be used with `/execute`"""
    JMC_COMMAND = auto()
    """Normal custom JMC function"""
    LOAD_ONCE = auto()
    """Can only be used on load function and used once"""
    LOAD_ONLY = auto()
    """Can only be used on load function"""
    VARIABLE_OPERATION = auto()
    """Returns a minecraft integer to a scoreboard variable"""


class JMCFunction:
    """
    Base function for all custom JMC function
    - Must be decorated by `@func_property`
    - Either call_bool (For BOOL_FUNCTION) or call (for other type) must be implemented

    Function types are
    - `FuncType.BOOL_FUNCTION`: returns a part of `/execute if` command
    - `FuncType.EXECUTE_EXCLUDED`: cannot be used with `/execute`
    - `FuncType.LOAD_ONCE`: can only be used on load function and used once
    - `FuncType.LOAD_ONLY`: can only be used on load function
    - `FuncType.VARIABLE_OPERATION`: returns a minecraft integer to a scoreboard variable
    - `FuncType.JMC_COMMAND`: normal custom JMC function

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
    __slots__ = ('arg_type', 'func_type', 'name',
                 'call_string', 'defaults', '_ignore',
                 'token', 'datapack', 'tokenizer',
                 'is_execute', 'var', 'args',
                 'raw_args')
    _decorated: bool = False
    """A private attribute that will be changed by a decorator to check for missing decorator (Set by decorator)"""
    arg_type: dict[str, ArgType]
    """Dictionary containing all parameter and it's ArgType (Set by decorator)"""
    func_type: FuncType
    """Type of the custom JMC function (Set by decorator)"""
    name: str
    """String for the function's name, for further use (Set by decorator)"""
    call_string: str
    """String that will be used in .jmc to call the function (Set by decorator)"""
    defaults: dict[str, str]
    """Defaults value of each parameter as string (Set by decorator)"""
    _ignore: set[str]
    """Private set of parameter for parser to ignore and leave as is (Set by decorator)"""

    token: Token
    """paren_round Token object containing the arguments"""
    datapack: DataPack
    """Datapack object"""
    tokenizer: Tokenizer
    """Current Tokenizer of the token"""
    is_execute: bool | None
    """Whether the function is in execute command (in VARIABLE_OPERATION, JMC_COMMANDS function type)"""
    var: str | None
    """Minecraft scoreboard variable for VARIABLE_OPERATION function to return"""

    args: dict[str, str]
    """Dictionary containing parameter and parsed argument in form of string"""
    raw_args: dict[str, Arg]
    """Dictionary containing parameter and given argument as Arg object"""

    __subcls: dict[FuncType, dict[str, type["JMCFunction"]]
                   ] = defaultdict(dict)
    """:cvar: Dictionary of (Function type and according dictionary of funtion name and a subclass)"""

    def __new__(cls, *args, **kwargs):
        if cls is JMCFunction:
            raise TypeError(
                f"Only children of '{cls.__name__}' may be instantiated")
        return super().__new__(cls)

    def __init__(self, token: Token, datapack: DataPack, tokenizer: Tokenizer,
                 *, is_execute: bool | None = None, var: str | None = None) -> None:
        self.token = token
        self.datapack = datapack
        self.tokenizer = tokenizer
        self.is_execute = is_execute
        self.var = var
        if not self._decorated:
            raise NotImplementedError("Missing decorator")
        if self.func_type is None:
            raise NotImplementedError("Missing func_type")

        args_Args = verify_args(self.arg_type,
                                self.call_string, token, tokenizer)
        self.args = {}
        self.raw_args = {}

        for key, arg in args_Args.items():
            if arg is None:
                if key not in self.defaults:
                    raise JMCMissingValueError(key, token, tokenizer)
                self.args[key] = self.defaults[key]
                continue

            self.raw_args[key] = arg
            if key in self._ignore:
                pass
            elif arg.arg_type == ArgType._FUNC_CALL:
                self.args[
                    key] = f"function {datapack.namespace}:{convention_jmc_to_mc(arg.token, self.tokenizer)}"
            elif arg.arg_type == ArgType.ARROW_FUNC:
                self.args[key] = '\n'.join(
                    datapack.parse_function_token(arg.token, tokenizer))
            elif arg.arg_type == ArgType.INTEGER:
                self.args[key] = arg.token.string
                # self.args[key] = str(find_scoreboard_player_type(
                #     arg.token, tokenizer).value)
            elif arg.arg_type == ArgType.FLOAT:
                self.args[key] = str(float(arg.token.string))
            elif arg.arg_type in {ArgType.SCOREBOARD_PLAYER, ArgType.SCOREBOARD}:
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
        This function will be called after initialization of the object
        """

    def call(self) -> str:
        """
        This function will be called when user call matching JMC custom function

        :raises NotImplementedError: When the subclass's call method is not implemented
        :return: Minecraft command as string
        """
        raise NotImplementedError("Call function not implemented")

    def call_bool(self) -> tuple[str, bool]:
        """
        This function will be called when user call matching JMC boolean(Can only be used in condition) function

        :raises NotImplementedError: When the subclass's call method is not implemented
        :return: Tuple of Minecraft command as string and boolean(True->if, False->unless)
        """
        raise NotImplementedError("Call(boolean) function not implemented")

    @classmethod
    def get_subclasses(
            cls, func_type: FuncType) -> dict[str, type["JMCFunction"]]:
        """
        Get dictionary of funtion name and a class matching function type

        :param func_type: Function type to search for
        :return: Dictionary of jmcfunction name and jmcfunction class
        """
        if func_type not in cls.__subcls:
            for subcls in cls.__subclasses__():
                cls.__subcls[subcls.func_type][subcls.call_string] = subcls

        return cls.__subcls[func_type]

    def is_never_used(self, call_string: str | None = None) -> bool:
        """
        Add current function to datapack.used_command and return whether it's already there

        :param: Any string instead of default call string for more specific check. For example, minecraft command
        :return: Whether this function has been called by the user before
        """
        if call_string is None:
            call_string = self.call_string
        is_in = call_string not in self.datapack.used_command
        self.datapack.used_command.add(call_string)
        return is_in

    def get_private_function(self, function_name: str) -> Function:
        """
        Get private function from self.datapack.private_functions

        :param function_name: Name of the private function
        :return: Function object
        """
        return self.datapack.private_functions[self.name][function_name]

    def make_empty_private_function(self, function_name: str) -> Function:
        """
        Make private function with no content

        :param function_name: Name of the function
        :return: Function object
        """
        func = self.datapack.private_functions[
            self.name][function_name] = Function()
        return func

    def load_arg_json(self, parameter: str) -> dict[str, Any]:
        """
        Get JSON argument from parameter name

        :param parameter: Name of the parameter of JMC function
        :raises JMCDecodeJSONError: Invalid JSON
        :return: JSON
        """
        try:
            json = loads(self.args[parameter])
        except JSONDecodeError as error:
            raise JMCDecodeJSONError(
                error, self.raw_args[parameter].token, self.tokenizer)

        return json


def func_property(func_type: FuncType, call_string: str, name: str, arg_type: dict[str, ArgType], defaults: dict[str, str] = {
}, ignore: set[str] = set()) -> Callable[[type[JMCFunction]], type[JMCFunction]]:
    """
    Decorator factory for setting property of custom JMC function

    :param func_type: Type of the custom JMC function
    :param call_string: String that will be used in .jmc to call the function
    :param name: String for the function's name, for further use
    :param arg_type: Dictionary containing all parameter and it's ArgType
    :param defaults: Defaults value of each parameter as string, defaults to {}
    :param ignore: Set of parameter for parser to ignore and leave as is
    :return: A decorator for JMCFunction class
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
        # for default in defaults:
        #     if default not in arg_type:
        #         raise BaseException()
        cls._ignore = ignore
        cls.name = name

        cls._decorated = True
        return cls
    return decorator
