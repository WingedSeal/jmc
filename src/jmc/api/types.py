from ..compile.datapack import DataPack
from dataclasses import dataclass as __dataclass
from ..terminal.configuration import GlobalData
from ..compile.header import Header
from ..compile.lexer import Lexer


@__dataclass(frozen=True, slots=True)
class Resource:
    type: str
    location: str
    content: str


@__dataclass(frozen=True, slots=True)
class Core:
    datapack: DataPack
    lexer: Lexer
    global_data: GlobalData
    header: Header
