from .utils import convention_jmc_to_mc
from .exception import JMCMissingValueError, JMCSyntaxException
from .header import Header
from .tokenizer import Token, Tokenizer
from .command.utils import Arg, ArgType, verify_args
from .datapack import DataPack, Function, PreFunction


class JMCDecorator:
    is_save_to_datapack: bool
    """Whether to save the function to datapack"""
    arg_type: dict[str, ArgType]
    """Dictionary containing all parameter and it's ArgType (Set by decorator)"""
    tokenizer: Tokenizer
    """Tokenizer"""
    token: Token
    """Decorator tokens"""
    call_string: str
    """String that will be used in to call the function (Set by decorator)"""
    raw_args: dict[str, Arg]
    """Dictionary containing parameter and given argument as Arg object"""
    args: dict[str, str]
    """Dictionary containing parameter and parsed argument in form of string"""
    defaults: dict[str, str]
    """Defaults value of each parameter as string (Set by decorator)"""
    datapack: DataPack
    """Datapack"""
    prefix: str
    """String of function prefix, aka. class it's currently in"""

    def __init__(self, tokenizer: Tokenizer, tokens: list[Token], datapack: DataPack, prefix: str,
                 arg_token: Token | None) -> None:
        self.tokens = tokens
        self.arg_token = arg_token
        self.tokenizer = tokenizer
        self.datapack = datapack
        self.prefix = prefix
        if arg_token:
            args_Args = verify_args(self.arg_type,
                                    self.call_string, arg_token, tokenizer)
            self.raw_args = {}
            self.args = {}

            for key, arg in args_Args.items():
                if arg is None:
                    if key not in self.defaults:
                        raise JMCMissingValueError(key, arg_token, tokenizer)
                    self.args[key] = self.defaults[key]
                    continue
                self.raw_args[key] = arg
                self.args[key] = arg.token.string

    def modify(self, pre_func: PreFunction, func: Function | None) -> None:
        raise NotImplementedError(
            "'modify' method of JMCDecorator not implemented")


DECORATORS: dict[str, type[JMCDecorator]] = {}


def dec_property(call_string: str,
                 arg_type: dict[str, ArgType] | None = None, defaults: dict[str, str] | None = None, is_save_to_datapack: bool = True):

    def decorator(cls: type[JMCDecorator]) -> type[JMCDecorator]:
        """
        A decorator to set the class's attributes for setting JMC decorator's properties

        :param cls: A subclass of JMCDecorator
        :return: Same class that was passed in
        """
        cls.is_save_to_datapack = is_save_to_datapack
        cls.arg_type = arg_type if arg_type is not None else {}
        cls.defaults = defaults if defaults is not None else {}
        cls.call_string = call_string
        DECORATORS[call_string] = cls
        return cls
    return decorator


@dec_property("add",
              arg_type={
                  "from": ArgType._FUNC_CALL
              })
class Add(JMCDecorator):
    def modify(self, pre_func: PreFunction, func: Function | None) -> None:
        call_from = convention_jmc_to_mc(
            self.raw_args["from"].token, self.tokenizer, self.prefix)
        if call_from == self.datapack.tick_name:
            self.datapack.after_ticks.append(
                f"function {self.datapack.format_func_path(pre_func.func_path)}")
            return
        if call_from == self.datapack.load_name:
            self.datapack.after_loads.append(
                f"function {self.datapack.format_func_path(pre_func.func_path)}")
            return

        self.datapack.after_func[call_from].append(
            f"function {self.datapack.format_func_path(pre_func.func_path)}")

        if self.arg_token is None:
            return
        self.datapack.after_func_token[call_from
                                       ] = self.raw_args["from"].token, self.tokenizer


@dec_property("lazy", is_save_to_datapack=False)
class Lazy(JMCDecorator):
    def modify(self, pre_func: PreFunction, func: Function | None) -> None:
        if pre_func.func_path in self.datapack.functions:
            old_function_token, old_function_tokenizer = self.datapack.defined_file_pos[
                pre_func.func_path]
            raise JMCSyntaxException(
                f"Duplicate function declaration({pre_func.func_path})", pre_func.self_token, pre_func.tokenizer,
                suggestion=f"This function was already defined at line {old_function_token.line} col {old_function_token.col} in {old_function_tokenizer.file_path}")
        self.datapack.lazy_func[pre_func.func_path] = pre_func


@dec_property("root")
class Root(JMCDecorator):
    def modify(self, pre_func: PreFunction, func: Function | None) -> None:
        pre_func.prefix = ""
