from json import dumps
from .log import Logger
from .header import Header
from .compile import read_cert, read_header, build
from .lexer import Lexer


logger = Logger(__name__)


class JMCPack:
    """
    Class representation of folder structure containing entire JMC files

    - Used for testing to prevent having to write and read files
    :param namespace: Namespace of the virtual datapack, defaults to "TEST"
    :param output: virtual directory for output, defaults to "VIRTUAL"
    """
    __slots__ = ('cert', 'jmc_file', 'header_file',
                 '__built', 'config')
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
        self.config = {
            "namespace": namespace,
            "description": "__THIS_IS_FOR_TESTING__",
            "pack_format": "10",
            "target": __file__,
            "output": output
        }

    def set_cert(self, file_content: str) -> "JMCPack":
        self.cert = file_content
        return self

    def set_jmc_file(self, file_content: str) -> "JMCPack":
        self.jmc_file = file_content
        return self

    def set_header_file(self, file_content: str) -> "JMCPack":
        self.header_file = file_content
        return self

    def build(self) -> "JMCPack":
        logger.info("Building from JMCPack")
        Header.clear()
        read_cert(self.config, _test_file=self.cert)
        read_header(self.config, _test_file=self.header_file)
        lexer = Lexer(self.config, _test_file=self.jmc_file)
        self.__built = build(lexer.datapack, self.config, _is_virtual=True)
        return self

    @property
    def built(self) -> dict[str, str]:
        if self.__built is None:
            self.build()
        if self.__built is None:
            raise ValueError("self.__built is None")
        return self.__built

    def dumps(self, *, indent: int = 4) -> str:
        return dumps(self.built, indent=indent)

    def to_string(self) -> str:
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
