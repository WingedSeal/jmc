from json import dumps

from .lexer import Lexer
from .log import Logger

logger = Logger(__name__)


def compile(config: dict[str, str]) -> None:
    logger.info("Configuration:\n"+dumps(config, indent=2))
    lexer = Lexer(config)
    logger.info(f'Datapack :{lexer.datapack!r}')
