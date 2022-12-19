"""Module handling jmc's header"""
from pathlib import Path
from typing import Callable, TYPE_CHECKING, Protocol

from .utils import SingleTon
from .log import Logger

if TYPE_CHECKING:
    from .tokenizer import Token

logger = Logger(__name__)


# class MacroFactory(Protocol):
#     """A function that takes in tuple of tokens(macro's argument) and current line and col then return list of tokens"""
#     __name__: str

#     def __call__(
#             self, argument_tokens: list["Token"], line: int, col: int) -> list["Token"]:
#         ...


MacroFactory = Callable[[list["Token"], int, int], list["Token"]]


class Header(SingleTon):
    """
    A SingleTon class containing all information from header
    """
    __slots__ = (
        'file_read',
        'macros',
        'credits',
        'is_enable_macro',
        'commands',
        'statics'
    )

    file_read: set[str]
    """Set of files that was already read (to prevent reading the same file multiple times"""
    macros: dict[str, tuple[MacroFactory, int]]
    """Dictionary of keyword to replace and tuple of (macro factory function and its amount of argument"""
    credits: list[str]
    """Dictionary of string to replace and what to replace it with"""
    is_enable_macro: bool
    """Whether to enable macro at the time of creating a token"""
    is_override_minecraft: bool
    """Whether to allow jmc to take control over minecraft namespace"""
    commands: set[str]
    """List of extra command(first arguments) to allow"""
    statics: set[Path]
    """All path that JMC will not remove"""

    def __init__(self) -> None:
        self.__clear(self)

    @classmethod
    def clear(cls) -> None:
        """
        Reset the single object
        """
        cls.__clear(cls())

    @staticmethod
    def __clear(obj: "Header"):
        obj.file_read = set()
        obj.macros = {}
        obj.credits = []
        obj.is_enable_macro = True
        obj.is_override_minecraft = False
        obj.commands = set()
        obj.statics = set()

    def add_file_read(self, path: Path) -> None:
        """
        Add path to file_read

        :param path: Path to file that's read
        """
        self.file_read.add(path.as_posix())

    def is_header_exist(self, path: Path) -> bool:
        """
        Check if header is already in file_read

        :param path: Path to check
        :return: Whether the file was already read
        """
        return path.as_posix() in self.file_read
