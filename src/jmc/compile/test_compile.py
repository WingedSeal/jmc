"""Module for testing compilation"""
from json import dumps
from pathlib import Path

from ..terminal.configuration import Configuration, GlobalData
from .log import Logger
from .header import Header
from .compiling import read_cert, read_header, build
from .lexer import Lexer


logger = Logger(__name__)


class JMCTestPack:
    """
    Class representation of folder structure containing entire JMC files

    - Used for testing to prevent having to write and read files

    :param namespace: Namespace of the virtual datapack, defaults to "TEST"
    :param output: virtual directory for output, defaults to "VIRTUAL"
    """
    __slots__ = ("cert", "jmc_file", "header_file",
                 "__built", "config")
    cert: str
    jmc_file: str
    header_file: str | None
    __built: dict[str, str] | None
    """Dictionary of file name and file content"""

    def __init__(self, namespace: str = "TEST",
                 output: str = "VIRTUAL") -> None:
        self.__built = None
        self.cert = """LOAD=__load__
TICK=__tick__
PRIVATE=__private__
VAR=__variable__
INT=__int__"""
        self.jmc_file = ""
        self.header_file = None
        self.config = Configuration(
            GlobalData(),
            namespace=namespace,
            description="__THIS_IS_FOR_TESTING__",
            pack_format="10",
            target=Path("main.jmc"),
            output=Path(output)
        )

    def set_pack_format(self, pack_format: int) -> "JMCTestPack":
        self.config.pack_format = str(pack_format)
        return self

    def set_cert(self, file_content: str) -> "JMCTestPack":
        """
        Set certificate(jmc.txt)

        :param file_content: File's content
        :return: Self
        """
        self.cert = file_content
        return self

    def set_jmc_file(self, file_content: str) -> "JMCTestPack":
        """
        Set main jmc file

        :param file_content: File's content
        :return: Self
        """
        self.jmc_file = file_content
        return self

    def set_header_file(self, file_content: str) -> "JMCTestPack":
        """
        Set main header file

        :param file_content: File's content
        :return: Self
        """
        self.header_file = file_content
        return self

    def build(self) -> "JMCTestPack":
        """
        Build datapack
        :return: Self
        """
        logger.info("Building from JMCPack")
        Header.clear()
        is_delete, cert_config, cert_file = read_cert(
            self.config, _test_file=self.cert)
        read_header(self.config, _test_file=self.header_file)
        lexer = Lexer(self.config, _test_file=self.jmc_file)
        built = build(
            lexer.datapack,
            self.config,
            is_delete, cert_config, cert_file,
            _is_virtual=True)
        if built is None:
            raise ValueError
        self.__built = {
            path.as_posix(): content for path,
            content in built.items()}
        return self

    @property
    def built(self) -> dict[str, str]:
        """Access built datapack"""
        if self.__built is None:
            self.build()
        if self.__built is None:
            raise ValueError("self.__built is None")
        return self.__built

    def dumps(self, *, indent: int = 4) -> str:
        """
        Dumps the built datapack into json formatted string

        :param indent: indentation, defaults to 4
        :return: JSON as string
        """
        return dumps(self.built, indent=indent)

    def to_string(self) -> str:
        """Get human-readable string"""
        return "\n".join(
            [f"> {file_name}\n{file_content}" for file_name, file_content in self.built.items()])

    def __str__(self) -> str:
        ouput_str = ""
        for key, value in self.built.items():
            ouput_str += f"""
=============================
{key}
-----------------------------
{value}
=============================
"""
        return ouput_str
