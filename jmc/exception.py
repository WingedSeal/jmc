from json import JSONDecodeError
from .log import Logger

logger = Logger(__name__)


def log(self: object, args: tuple):
    logger.warning(f"{self.__class__.__name__}\n{args[0]}")


class JMCSyntaxException(SyntaxError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCSyntaxWarning(SyntaxWarning):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCFileNotFoundError(FileNotFoundError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCBuildError(Exception):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class JMCDecodeJSONError(ValueError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)


class MinecraftSyntaxWarning(SyntaxError):
    def __init__(self, *args: object) -> None:
        log(self, args)
        super().__init__(*args)
