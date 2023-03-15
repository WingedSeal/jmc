from .tokenizer import Token
from .command.utils import ArgType
from .datapack import Function


class JMCDecorator:
    is_save_to_datapack: bool
    """Whether to save the function to datapack"""
    arg_type: dict[str, ArgType]
    """Dictionary containing all parameter and it's ArgType (Set by decorator)"""

    def __init__(self, arg_token: Token | None) -> None:
        self.arg_token = arg_token
        pass

    def modify(self, func: Function) -> None:
        raise NotImplementedError(
            "'modify' method of JMCDecorator not implemented")


DECORATORS: dict[str, type[JMCDecorator]] = {}


def dec_property(call_string: str,
                 arg_type: dict[str, ArgType] | None = None, is_save_to_datapack: bool = True):

    def decorator(cls: type[JMCDecorator]) -> type[JMCDecorator]:
        """
        A decorator to set the class's attributes for setting JMC decorator's properties

        :param cls: A subclass of JMCDecorator
        :return: Same class that was passed in
        """
        cls.is_save_to_datapack = is_save_to_datapack
        cls.arg_type = arg_type if arg_type is not None else {}
        DECORATORS[call_string] = cls
        return cls
    return decorator


@dec_property("add",
              arg_type={})
class Add(JMCDecorator):
    def modify(self, func: Function) -> None:
        print(self.arg_token)
