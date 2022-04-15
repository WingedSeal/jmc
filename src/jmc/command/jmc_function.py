from enum import Enum, auto
from functools import wraps
from typing import Optional

from .utils import ArgType, find_scoreboard_player_type, verify_args
from ..datapack import DataPack
from ..exception import JMCTypeError
from ..tokenizer import Token, Tokenizer, TokenType


class FuncType(Enum):
    bool_function = auto()
    execute_excluded = auto()
    jmc_command = auto()
    load_once = auto()
    load_only = auto()


class JMCFunction:
    _decorated = False
    arg_type: dict[str, ArgType]
    func_type: FuncType = None
    name: str
    call_string: str
    defaults: dict[str, str] = dict()

    def __init__(self, token: Token, datapack: DataPack, tokenizer: Tokenizer, is_execute: Optional[bool] = None) -> None:
        self.token = token
        self.datapack = datapack
        self.tokenizer = tokenizer
        self.is_execute = is_execute
        if self.func_type is None:
            raise NotImplementedError("missing func_type")

        self._args = verify_args(self.arg_type,
                                 self.call_string, token, tokenizer)
        self.args: dict[str, str] = dict()

        for key, arg in self._args.items():
            if arg is None:
                if key not in self.defaults:
                    raise JMCTypeError(key, token, tokenizer)
                self.args[key] = self.defaults[key]
            else:
                if arg.arg_type == ArgType._func_call:
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
                    self.args[key] = f"{scoreboard_player.value[1]} {scoreboard_player.value[0]}"
                else:
                    self.args[key] = arg.token.string

        self.__post__init__()

    def __post__init__(self) -> None:
        pass

    def call(self) -> str:
        raise NotImplementedError("call function not implemented")

    @classmethod
    def _get(cls, func_type: FuncType) -> dict[str, "JMCFunction"]:
        commands = dict()
        for subcls in cls.__subclasses__():
            if subcls.func_type == func_type:
                commands[subcls.call_string] = subcls
        return commands
