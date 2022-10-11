from pathlib import Path

from .utils import SingleTon
from .exception import HeaderDuplicatedMacro, HeaderFileNotFoundError, HeaderSyntaxException
from .log import Logger

logger = Logger(__name__)


class Header(SingleTon):
    """
    A SingleTon class containing all information from header
    """
    file_read: set[str] = set()
    """Set of files that was already read (to prevent reading the same file multiple times"""
    macros: dict[str, str] = {}
    """Dictionary of keyword to replace and what to replace it with"""
    replaces: dict[str, str] = {}
    """Dictionary of string to replace and what to replace it with"""

    @classmethod
    def clear(cls) -> None:
        """
        Reset the single object
        """
        self = cls()
        self.file_read = set()
        self.macros = {}
        self.replaces = {}

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


def parse_header(header_str: str, file_name: str, parent_target: Path) -> Header:
    """
    Parse header and store the information in the header object

    :param header_str: String that was read from the file
    :param file_name: Header file's name
    :param parent_target: Path to parent of the main jmc file
    :raises HeaderSyntaxException: A line in the file doesn't start with '#'
    :raises HeaderDuplicatedMacro: Define same macro twice
    :raises HeaderSyntaxException: Too many/little argument for define
    :raises HeaderSyntaxException: File name isn't wrapped in quote or angle bracket (For `#include`)
    :raises HeaderFileNotFoundError: Can't find header file
    :raises HeaderSyntaxException: Include same file twice
    :raises HeaderSyntaxException: Whitespace found in header file's name
    :raises NotImplementedError: WORKING ON `#replace`
    :raises NotImplementedError: WORKING ON `#credit`
    :raises HeaderSyntaxException: Directive (`#something`) is unrecognized
    :return: Header singleton object

    .. TODO::
        implement replace and credit

    """
    header = Header()
    lines = header_str.split("\n")
    for line, line_str in enumerate(lines):
        line += 1
        if line_str.isspace() or line_str.startswith("//") or line_str=="":
            continue

        if not line_str.startswith("#"):
            raise HeaderSyntaxException(
                "Expected '#'", file_name, line, line_str)

        directive = line_str[1:]
        args = directive.split()

        if args[0] == "define":
            if len(args) == 3:
                key = args[1]
                value = args[2]
                logger.debug(f'Define "{key}" as "{value}"')
                if key in header.macros:
                    raise HeaderDuplicatedMacro(
                        f"'{key}' macro is already defined", file_name, line, line_str)
                header.macros[key] = value
            else:
                raise HeaderSyntaxException(
                    f"'define' takes 2 arguments (got {len(args)-1})", file_name, line, line_str)

        elif args[0] == "include":
            if len(args) == 2:
                included = args[1]
                if (
                    not (included.startswith("<") and included.endswith(">"))
                    and
                    not (included.startswith('"') and included.endswith('"'))
                ):
                    raise HeaderSyntaxException(
                        "Included file must be wrapped in double quotes `\"` or angle bracket `<>`", file_name, line, line_str)
                file_name = included[1:-1]
                if not file_name.endswith(".hjmc"):
                    file_name += ".hjmc"
                header_file = parent_target/file_name
                if not header_file.is_file():
                    raise HeaderFileNotFoundError(header_file)
                with header_file.open('r') as file:
                    header_str = file.read()
                logger.info(f"Parsing {header_file}")
                if header.is_header_exist(header_file):
                    raise HeaderSyntaxException(
                        f"File {header_file.as_posix()} is already included.", file_name, line, line_str)
                header.add_file_read(header_file)
                parse_header(header_str, header_file.as_posix(), parent_target)
            else:
                raise HeaderSyntaxException(
                    "Whitespace is not supported in header file name", file_name, line, line_str)

        elif args[0] == "replace":
            raise NotImplementedError("Replace feature hasn't been implemented yet.")

        elif args[0] == "credit":
            raise NotImplementedError("Credit feature hasn't been implemented yet.")

        else:
            raise HeaderSyntaxException(
                f"Unrecognized directive '{args[0]}'", file_name, line, line_str)
    return header
