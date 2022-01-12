from pathlib import Path
import json

from . import Logger
import logging
from typing import List, Set, TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from .module import Module
    from .function import Function


logger = Logger(__name__)


class PackGlobal:
    def __init__(self, target_file: Path) -> None:
        self.target_path = target_file.parent
        self.pack_path = target_file.parent/Path('compiled')
        self.scoreboards: Set[str] = {'__int__', '__variable__'}
        self.ints: Set[int] = set()
        self.functions: Dict[str, Function] = dict()
        self.imports: List[Module] = []
        self.namespace: str = 'TEST'
        self.pack_format: int = 7
        self.description: str = 'DESC'

    def __str__(self) -> str:
        nl = '\n'
        return f"""PackGlobal
        Target Path (.jmc): {self.target_path.resolve()}
        Datapack Directory (Exported): {self.pack_path.resolve()}
        Scoreboards: {self.scoreboards}
        Integers: {self.ints}
        Functions: {nl.join([str(_function) for _function in self.functions.values()])}
        Imports: {nl.join([str(imported) for imported in self.imports])}
        """

    def compile(self) -> None:
        logger.info("Compiling, Exporting to files")
        self.pack_path.mkdir(exist_ok=True)
        with (self.pack_path/'pack.mcmeta').open(mode='w+') as file:
            json.dump({
                "pack": {
                      "pack_format": self.pack_format,
                      "description": self.description
                      }
            }, file, indent=2)
        minecraft_function_path = self.pack_path/'data'/'minecraft'/'tags'/'funtions'
        namespace_path = self.pack_path/'data'/self.namespace
        function_path = namespace_path/'functions'

        minecraft_function_path.mkdir(exist_ok=True, parents=True)
        namespace_path.mkdir(exist_ok=True, parents=True)
        function_path.mkdir(exist_ok=True, parents=True)

        # Handle __load__
        __load__ = "\n".join(
            [f'scoreboard objectives add {obj} dummy' for obj in self.scoreboards] +
            [command.text for command in self.functions["__load__"].context]
        )
        with (minecraft_function_path/'load.json').open(mode='w+') as file:
            string = file.read()
            if string == "":
                dictionary = {"values": []}
            else:
                dictionary: dict = json.loads(string)
            dictionary["replace"] = False
            dictionary["values"].append(f"{self.namespace}:__load__")
            json.dump(dictionary, file)
        with (function_path/'__load__.mcfunction').open(mode='w+') as file:
            file.write(__load__)
