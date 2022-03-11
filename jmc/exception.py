from json import JSONDecodeError
from .log import Logger

logger = Logger(__name__)


class JMCSyntaxException(SyntaxError):
    def __init__(self, *args: object) -> None:
        logger.warning(f"JMCSyntaxException\n{args[0]}")
        super().__init__(*args)


class JMCFileNotFoundError(FileNotFoundError):
    def __init__(self, *args: object) -> None:
        logger.warning(f"JMCFileNotFoundError\n{args[0]}")
        super().__init__(*args)


class JMCDecodeJSONError(ValueError):
    def __init__(self, *args: object) -> None:
        logger.warning(f"JMCDecodeJSONError\n{args[0]}")
        super().__init__(*args)
