from collections import defaultdict
from json import dumps
from .tokenizer import Token
from .log import Logger

logger = Logger(__name__)


class DataPack:
    PRIVATE_STR = '__private__'
    LOAD_NAME = '__load__'
    TICK_NAME = '__tick__'

    def __init__(self, namespace: str) -> None:
        logger.debug("Initializing Datapack")
        self.ints: set[int] = set()
        self.functions: dict[str, list[str]] = dict()
        self.load_function: list[list[Token]] = []
        self.jsons: dict[str, dict[str, dict]] = defaultdict(dict)
        self.private_functions: dict[str,
                                     dict[str, list[str]]] = defaultdict(dict)

        self.loads: list[str] = []
        self.ticks: list[str] = []
        self.namespace = namespace

    def __repr__(self) -> str:
        return f"""DataPack(
    PRIVATE_STR = {self.PRIVATE_STR},
    LOAD_NAME = {self.LOAD_NAME},
    TICK_NAME = {self.TICK_NAME},
    
    ints = {self.ints!r}
    function = 
{dumps(self.functions, indent=2)}
    jsons =
{dumps(self.jsons, indent=2)}
    private_functions = 
{dumps(self.private_functions, indent=2)}

)"""
