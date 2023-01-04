
"""Module for testing compilation"""
from dataclasses import dataclass as __dataclass
from pathlib import Path

from .datapack import DataPack
from .lexer import Lexer

from ..terminal.configuration import Configuration, GlobalData
from .header import Header
from .compiling import read_cert, read_header, build


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


class PyJMC:
    files: dict[Path, str]
    """Dictionary of path to the file and its content"""
    resource_locations: list[Resource]
    """List of resource_type, resource_location and the content"""
    namespace: str
    """Datapack namespace"""
    config: Configuration
    """Configuration of the JMC workspace"""
    core: Core
    """Inner working of JMC"""

    def __init__(self, namespace: str, description: str,
                 pack_format: str, target: str) -> None:
        self.config = Configuration(
            GlobalData(),
            namespace=namespace,
            description=description,
            pack_format=pack_format,
            target=Path(target),
            output=Path("Virtual-PyJMC")
        )

        self.__build()

    def __build(self) -> None:
        """
        Build datapack
        :return: Self
        """
        Header.clear()
        read_cert(self.config)
        read_header(self.config)
        lexer = Lexer(self.config)
        datapack = lexer.datapack
        built = build(datapack, self.config, _is_virtual=True)
        if built is None:
            raise ValueError("Lexer.built return None")
        self.files = built
        self.namespace = datapack.namespace
        self.resource_locations = []
        for path, content in self.files.items():
            relative_path = path.relative_to(self.config.output)
            if relative_path.parents[-2] == "tags":
                resource_type = f"tags/{relative_path.parents[-3].as_posix()}"
            else:
                resource_type = relative_path.parents[-2].as_posix()

            resource_location = f'{self.namespace}:{relative_path.relative_to(resource_type).with_suffix("").as_posix()}'
            self.resource_locations.append(
                Resource(resource_type, resource_location, content))
        self.core = Core(datapack, lexer, self.config.global_data, Header())


__all__ = ["PyJMC"]
