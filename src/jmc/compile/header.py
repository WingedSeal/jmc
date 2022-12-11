"""Module handling jmc's header"""
from pathlib import Path

from .utils import SingleTon
from .log import Logger

logger = Logger(__name__)


class Header(SingleTon):
    """
    A SingleTon class containing all information from header
    """
    __slots__ = ('file_read', 'macros', 'credits', 'is_enable_macro')

    file_read: set[str]
    """Set of files that was already read (to prevent reading the same file multiple times"""
    macros: dict[str, str]
    """Dictionary of keyword to replace and what to replace it with"""
    credits: list[str]
    """Dictionary of string to replace and what to replace it with"""
    is_enable_macro: bool
    """Whether to enable macro at the time of creating a token"""

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
