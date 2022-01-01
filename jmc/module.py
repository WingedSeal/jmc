from pathlib import Path
import re
from typing import List
from . import Logger, PackGlobal
import logging

logger = Logger(__name__)


class Module:
    """Module from @import command"""

    def __init__(self, path: str, pack_global: PackGlobal) -> None:
        path: Path = pack_global.target_path/path
        self.name = Path(path).stem
        self.path = pack_global.pack_path / f'{self.name}.mcfunction'
        try:
            with path.open() as file:
                self.context = file.read()
        except FileNotFoundError as error:
            self.context = ''
            logger.warning(
                f"File not found for module, {path}\n{error}")
        logger.info(
            f'importing from "{path}" to "{self.path}"')

    def __str__(self) -> str:
        return f"{self.name} Module({self.path.resolve()})"

    def __repr__(self) -> str:
        return f"<Module path='{self.path.resolve()}'>"
