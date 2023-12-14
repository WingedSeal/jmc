"""Module handling jmc's header"""
from pathlib import Path
from typing import Any, Callable, TYPE_CHECKING

from .utils import SingleTon
from .log import Logger

if TYPE_CHECKING:
    from .tokenizer import Token
    from ..compile.datapack import DataPack

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
        "file_read",
        "macros",
        "number_macros",
        "credits",
        "is_enable_macro",
        "commands",
        "statics",
        "dels",
        "post_process",
        "finished_compiled_time",
        "nometa"
    )

    file_read: set[str]
    """Set of files that was already read (to prevent reading the same file multiple times"""
    macros: dict[str, tuple[MacroFactory, int]]
    """Dictionary of keyword to replace and tuple of (macro factory function and its amount of argument"""
    number_macros: dict[str, str]
    """Dictionary of text to replace and number to replace with, used in Hardcode.calc"""
    credits: list[str]
    """Dictionary of string to replace and what to replace it with"""
    is_enable_macro: bool
    """Whether to enable macro at the time of creating a token"""
    namespace_overrides: set[str]
    """Whether to allow jmc to take control over minecraft namespace"""
    commands: set[str]
    """List of extra command(first arguments) to allow"""
    statics: set[Path]
    """All path that JMC will not remove"""
    dels: set[str]
    """List of exception to command(first arguments) to ignore"""
    post_process: list[Callable[["DataPack"], Any]]
    """Python function to run before building datapack"""
    finished_compiled_time: float
    nometa: bool
    """Whether hand pack.mcmeta to user"""

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
        obj.number_macros = {}
        obj.credits = []
        obj.is_enable_macro = True
        obj.namespace_overrides = set()
        obj.commands = set()
        obj.statics = set()
        obj.dels = set()
        obj.post_process = []
        obj.finished_compiled_time = 0
        obj.nometa = False

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
