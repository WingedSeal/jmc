from collections import defaultdict
from enum import Enum, auto
from json import JSONDecodeError, loads
from typing import TYPE_CHECKING, Any, Callable

from ..utils import convention_jmc_to_mc, is_float
from ..datapack_data import Item, SIMPLE_JSON_BODY
from .utils import ArgType, FormattedText, NumberType, find_scoreboard_player_type, hash_string_to_string, verify_args, Arg
from ..datapack import DataPack, Function
from ..exception import JMCDecodeJSONError, JMCMissingValueError, JMCValueError
from ..tokenizer import Token, TokenType, Tokenizer


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
    __slots__ = ("token", "datapack", "tokenizer",
                 "is_execute", "var", "args",
                 "raw_args", "self_token", "prefix")
    # _decorated: bool = False
    # """A private attribute that will be changed by a decorator to check for missing decorator (Set by decorator)"""
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
    number_type: dict[str, NumberType]
    """Dictionary containing some number parameter that need to be specific (Set by decorator)"""
    _ignore: set[str]
    """Private set of parameter for parser to ignore and leave as is (Set by decorator)"""

    token: Token
    """paren_round Token object containing the arguments"""
    self_token: Token
    """keyword Token object of the call string"""
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

    _subcls: dict[FuncType, dict[str, type["JMCFunction"]]
                  ] = defaultdict(dict)
    """:cvar: Dictionary of (Function type and according dictionary of funtion name and a subclass)"""

    prefix: str
    """String of function prefix, aka. class it's currently in"""

    def __new__(cls, *args, **kwargs):
        if cls is JMCFunction:
            raise TypeError(
                f"Only children of '{cls.__name__}' may be instantiated")
        return super().__new__(cls)

    def __init__(self, token: Token, self_token: Token, datapack: DataPack, tokenizer: Tokenizer, prefix: str,
                 *, is_execute: bool | None = None, var: str | None = None) -> None:
        self.token = token
        self.self_token = self_token
        self.datapack = datapack
        self.tokenizer = tokenizer
        self.is_execute = is_execute
        self.var = var
        self.prefix = prefix

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
                if ":" in arg.token.string:
                    self.args[key] = f"function {arg.token.string}"
                else:
                    self.args[
                        key] = f"function {datapack.format_func_path(convention_jmc_to_mc(arg.token, self.tokenizer, self.prefix))}"
            elif arg.arg_type == ArgType.ARROW_FUNC:
                self.args[key] = "\n".join(
                    datapack.parse_function_token(arg.token, tokenizer, prefix))
            elif arg.arg_type == ArgType.FLOAT:
                self.args[key] = str(float(arg.token.string))
            elif arg.arg_type in {ArgType.SCOREBOARD_INT, ArgType.SCOREBOARD}:
                scoreboard_player = find_scoreboard_player_type(
                    arg.token, tokenizer)
                if isinstance(scoreboard_player.value, int):
                    raise ValueError(
                        "scoreboard_player.value is int for minecraft scorboard")
                self.args[key] = f"{scoreboard_player.value[1]} {scoreboard_player.value[0]}"
            else:
                self.args[key] = arg.token.string

        for parameter, number_type in self.number_type.items():
            if self.arg_type[parameter] == ArgType.SCOREBOARD_INT:
                if not is_float(self.args[parameter]):
                    continue

            elif self.arg_type[parameter] not in {
                    ArgType.INTEGER, ArgType.FLOAT}:
                raise ValueError(f"{parameter} paremeter is not number")

            if number_type == NumberType.POSITIVE:
                if float(self.args[parameter]) <= 0:
                    raise JMCValueError(
                        f"{parameter} can only be {number_type.value}",
                        self.raw_args[parameter].token,
                        tokenizer)
            elif number_type == NumberType.ZERO_POSITIVE:
                if float(self.args[parameter]) < 0:
                    raise JMCValueError(
                        f"{parameter} can only be {number_type.value}",
                        self.raw_args[parameter].token,
                        tokenizer)

            elif number_type == NumberType.NON_ZERO:
                if float(self.args[parameter]) == 0:
                    raise JMCValueError(
                        f"{parameter} can only be {number_type.value}",
                        self.raw_args[parameter].token,
                        tokenizer)

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

    def call_bool(self) -> tuple[str, bool, list[str]]:
        """
        This function will be called when user call matching JMC boolean(Can only be used in condition) function

        :raises NotImplementedError: When the subclass's call method is not implemented
        :return: Tuple of Minecraft command as string and boolean(True->if, False->unless) and list of precommands
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
        return cls._subcls[func_type]

    def is_never_used(self, call_string: str | None = None,
                      parameters: list[str] | None = None) -> bool:
        """
        Add current function to datapack.used_command and return whether it's not already there

        :param call_string: Any string instead of default call string for more specific check. For example, minecraft command, defaults to self.call_string
        :param parameters: Details of call_string
        :return: Whether this function has never been called by the user before
        """
        if call_string is None:
            call_string = self.call_string
        if parameters is not None:
            call_string = call_string + '/' + '/'.join(parameters)
        is_not_in = call_string not in self.datapack.used_command
        self.datapack.used_command.add(call_string)
        return is_not_in

    def get_private_function(self, function_name: str) -> Function:
        """
        Get private function from self.datapack.private_functions

        :param function_name: Name of the private function
        :return: Function object
        """
        return self.datapack.private_functions[self.name][function_name]

    def format_text(self, parameter: str, is_default_no_italic: bool = False,
                    is_allow_score_selector: bool = True) -> str:
        """
        Get FormattedText string from an argument

        :param parameter: Parameter
        :param is_default_no_italic: Whether to set italic to False by default, defaults to False
        :param is_allow_score_selector: Whether to allow score selector in the string, defaults to True
        :return: Raw json string
        """
        return str(
            FormattedText(
                self.args[parameter],
                self.raw_args[parameter].token,
                self.tokenizer,
                self.datapack,
                is_default_no_italic=is_default_no_italic,
                is_allow_score_selector=is_allow_score_selector)
        )

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
            json = loads(self.args[parameter], strict=False)
        except JSONDecodeError as error:
            raise JMCDecodeJSONError(
                error, self.raw_args[parameter].token, self.tokenizer) from error

        return json

    def check_bool(self, parameter: str) -> bool:
        """
        Check if argument is true or false

        :param parameter: String parameter
        :raises JMCValueError: Argument is invalid
        :return: Whether argument is true
        """
        if self.args[parameter] not in {"true", "false"}:
            raise JMCValueError(
                f"'{parameter}' only accepts true or false in {self.call_string}",
                self.raw_args[parameter].token,
                self.tokenizer)
        return self.args[parameter] == "true"

    def add_formatted_text_prop(self, key: str, body: SIMPLE_JSON_BODY | Callable[[str], SIMPLE_JSON_BODY],
                                is_local: bool, property_name="propertyName"):
        """
        Add property of FormattedText to `datapack.data`

        :param key: Key of the minecraft json, (clickEvent etc.)
        :param body: Body of the minecraft json
        :param is_local: Whether to delete the property after one use
        :param property_name: Parameters to access `self.args` , defaults to "propertyName"
        """
        if self.args[property_name] in self.datapack.data.formatted_text_prop:
            raise JMCValueError(
                f"Text's property '{self.args[property_name]}' was already defined",
                self.raw_args["propertyName"].token, self.tokenizer)
        self.datapack.data.formatted_text_prop[self.args[property_name]] = (
            key, body, is_local)

    def require(self, pack_format: int, suggestion: str | None = None):
        """
        Raise MinecraftVersionTooLow when pack_format is too low, a shortcut for `self.datapack.version.require`

        :param pack_format: required pack_format
        :param suggestion: error suggestion, defaults to None
        """
        self.datapack.version.require(
            pack_format, self.self_token, self.tokenizer, suggestion=suggestion)


def func_property(func_type: FuncType, call_string: str, name: str, arg_type: dict[str, ArgType], defaults: dict[str, str] = {
}, ignore: set[str] = set(), number_type: dict[str, NumberType] = {}) -> Callable[[type[JMCFunction]], type[JMCFunction]]:
    """
    Decorator factory for setting property of custom JMC function

    :param func_type: Type of the custom JMC function
    :param call_string: String that will be used in .jmc to call the function
    :param name: String for the function's name, for further use
    :param arg_type: Dictionary containing all parameter and it's ArgType
    :param defaults: Defaults value of each parameter as string, defaults to {}
    :param ignore: Set of parameter for parser to ignore and leave as is, defaults to set()
    :param number_type: Dictionary containing some number parameter that need to be specific, defaults to {}
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
        cls.number_type = number_type
        # for default in defaults:
        #     if default not in arg_type:
        #         raise BaseException()
        cls._ignore = ignore
        cls.name = name

        # cls._decorated = True
        JMCFunction._subcls[func_type][call_string] = cls
        return cls
    return decorator
