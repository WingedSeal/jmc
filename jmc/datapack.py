from collections import defaultdict
from .log import Logger

logger = Logger(__name__)


class Function:
    def __init__(self, commands: list[str]) -> None:
        self.commands = commands

    def __repr__(self) -> str:
        return f"Function(commands={repr(self.commands)})"


class DataPack:
    ints: set[int] = set()
    functions: dict[str, Function] = dict()
    jsons: dict[str, dict[str, dict]] = defaultdict(dict)
    private_functions: dict[str, dict[str, Function]] = defaultdict(dict)

    loads: list[str] = []
    ticks: list[str] = []

    def __init__(self, namespace: str) -> None:
        logger.debug("Initializing Datapack")
        self.namespace = namespace
