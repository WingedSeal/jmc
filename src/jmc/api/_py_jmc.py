from dataclasses import dataclass
from pathlib import Path

from ..compile.datapack import DataPack
from ..compile.lexer import Lexer

from ..terminal.configuration import Configuration, GlobalData
from ..compile.header import Header
from ..compile.compiling import cert_config_to_string, read_cert, read_header, build


@dataclass(frozen=True, slots=True)
class Resource:
    """Resource location's data"""
    type: str
    location: str
    content: str


@dataclass(frozen=True, slots=True)
class Core:
    """Inner working of JMC"""
    datapack: DataPack
    lexer: Lexer
    global_data: GlobalData
    header: Header


class PyJMC:
    """
    Class representing JMC pack

    :param namespace: Datapack namespace
    :param description: Datapack description
    :param pack_format: pack_format
    :param target: Path of main jmc file
    :param jmc_txt: jmc.txt content, defaults to { "LOAD": "__load__", "TICK": "__tick__", "PRIVATE": "__private__", "VAR": "__variable__", "INT": "__int__", "STORAGE": "__storage__" }
    """
    __slots__ = ("files",
                 "resource_locations",
                 "namespace",
                 "config",
                 "core",
                 "pack_mcmeta",
                 "_cert_file")
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
    pack_mcmeta: dict[str, dict[str, int | str]]
    """Content of pack.mcmeta file"""
    _cert_file: str

    def __init__(self, namespace: str, description: str,
                 pack_format: str, target: str, jmc_txt: dict[str, str] = {
                     "LOAD": "__load__",
                     "TICK": "__tick__",
                     "PRIVATE": "__private__",
                     "VAR": "__variable__",
                     "INT": "__int__",
                     "STORAGE": "__storage__"
                 }) -> None:
        self.config = Configuration(
            GlobalData(),
            namespace=namespace,
            description=description,
            pack_format=pack_format,
            target=Path(target),
            output=Path("Virtual-PyJMC")
        )

        self._cert_file = cert_config_to_string(jmc_txt)
        self.__build()
        self.pack_mcmeta = {"pack": {
            "pack_format": int(self.config.pack_format),
            "description": self.config.description
        }}

    def __build(self) -> None:
        """
        Build datapack
        :return: Self
        """
        Header.clear()
        is_delete, cert_config, cert_file = read_cert(
            self.config, _test_file=self._cert_file)
        read_header(self.config)
        lexer = Lexer(self.config)
        datapack = lexer.datapack
        built = build(
            datapack,
            self.config,
            is_delete,
            cert_config,
            cert_file,
            _is_virtual=True)
        if built is None:
            raise ValueError("Lexer.built return None")
        self.files = built
        self.namespace = datapack.namespace
        self.resource_locations = []
        for path, content in self.files.items():
            relative_path = path.relative_to(self.config.output / "data")
            if relative_path.parts[1] == "tags":
                resource_type = "/".join(relative_path.parts[1:3])
                resource_path = "/".join(
                    relative_path.parts[3:-1] + (relative_path.stem, ))
            else:
                resource_type = relative_path.parts[1]
                resource_path = "/".join(
                    relative_path.parts[2:-1] + (relative_path.stem, ))
            namespace = relative_path.parts[0]

            # f'{namespace}:{relative_path.relative_to(resource_type).with_suffix("").as_posix()}'
            resource_location = f"{namespace}:{resource_path}"
            self.resource_locations.append(
                Resource(resource_type, resource_location, content))
        self.core = Core(datapack, lexer, self.config.global_data, Header())


__all__ = ["PyJMC"]
