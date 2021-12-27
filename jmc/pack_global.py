from pathlib import Path
from . import Logger
import logging
from typing import List, Set, TYPE_CHECKING
if TYPE_CHECKING:
    from .module import Module


logger = Logger(__name__, logging.INFO)


class PackGlobal:
    def __init__(self, target_file: Path) -> None:
        self.target_path = target_file.parent
        self.pack_path = target_file.parent/Path('compiled')
        self.scoreboards: Set[str] = {'__int__', '__variable__'}
        self.ints: Set[int] = set()
        self.functions_name: Set[str] = set()
        self.imports: List[Module] = []

    def __str__(self) -> str:
        nl = '\n'
        return f"""PackGlobal
        Target Path (.jmc): {self.target_path.resolve()}
        Datapack Directory (Exported): {self.pack_path.resolve()}
        Scoreboards: {self.scoreboards}
        Integers: {self.ints}
        Functions: {self.functions_name}
        Imports: {nl.join([str(imported) for imported in self.imports])}
        """
