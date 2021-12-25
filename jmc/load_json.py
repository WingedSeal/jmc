from . import Logger
import logging
from typing import Set

logger = Logger(__name__, logging.INFO)


class LoadJson:
    def __init__(self) -> None:
        self.scoreboards: Set[str] = {"INT"}
        self.ints: Set[int] = set()
        self.functions_name: Set[str] = set()

    def __str__(self) -> str:
        return f"""LoadJson
        Scoreboards: {self.scoreboards}
        Integers: {self.ints}
        Functions: {self.functions_name}"""
