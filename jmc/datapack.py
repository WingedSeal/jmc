from collections import defaultdict
from json import dumps
from .tokenizer import Token
from .log import Logger

logger = Logger(__name__)


class DataPack:
    PRIVATE_STR = '__private__'
    LOAD_NAME = '__load__'
    TICK_NAME = '__tick__'

    ints: set[int] = set()
    functions: dict[str, list[str]] = dict()
    load_function: list[list[Token]] = []
    jsons: dict[str, dict[str, dict]] = defaultdict(dict)
    private_functions: dict[str, dict[str, list[str]]] = defaultdict(dict)

    loads: list[str] = []
    ticks: list[str] = []

    def __init__(self, namespace: str) -> None:
        logger.debug("Initializing Datapack")
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
