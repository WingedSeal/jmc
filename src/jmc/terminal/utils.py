from enum import Enum
from getpass import getpass
from threading import Event
from traceback import format_exc
from ..compile import Logger

logger = Logger(__name__)


class Colors(Enum):
    HEADER = "\033[1;33;40m"
    YELLOW = "\033[33;40m"
    INFO = "\033[94;40m"
    INPUT = "\033[96;40m"
    PURPLE = "\033[35;40m"
    FAIL = "\033[91;40m"
    FAIL_BOLD = "\033[1;91;40m"
    ENDC = "\033[0;0;40m"
    EXIT = "\033[0;0;0m"
    NONE = "\033[0;37;40m"


def pprint(values, color: Colors = Colors.NONE):
    """
    Print but with colors

    :param values: Value for printing
    :param color: color of printing
    """
    print(f"{color.value}{values}{Colors.ENDC.value}")


def get_input(prompt: str = "> ", color: Colors = Colors.INPUT) -> str:
    """
    Get an input from user

    :param promt: Display string infront
    :param color: Color of the input and promt
    :return: input from user
    """
    input_value = input(f"{color.value}{prompt}")
    print(Colors.ENDC.value, end="")
    logger.info(f"Input from user: {input_value}")
    return input_value


def press_enter(prompt: str, color: Colors = Colors.INPUT) -> None:
    """
    Wait for Enter key from user

    :param prompt: Display string
    :param color: Color of prompt
    """
    getpass(f"{color.value}{prompt}{Colors.ENDC.value}")


def error_report(error: Exception) -> None:
    """
    Report error to user

    :param error: Exception for reporting
    """
    pprint(type(error).__name__, Colors.FAIL_BOLD)
    pprint(error, Colors.FAIL)


def handle_exception(error: Exception, event: Event, is_ok: bool):
    """
    Tell user when unexpected crash happens and reset

    :param error: Exception
    :param event: Event object to stop compiling
    :param is_ok: Whether to tell user this error is normal
    """
    event.set()
    pprint("Unexpected error causes program to crash", Colors.FAIL)
    pprint(type(error).__name__, Colors.FAIL_BOLD)
    pprint(error, Colors.FAIL)
    if not is_ok:
        pprint(format_exc(), Colors.YELLOW)
        pprint(
            "Please report this error at https://github.com/WingedSeal/jmc/issues/new/choose or https://discord.gg/PNWKpwdzD3.",
            Colors.FAIL)
    logger.critical("Program crashed")
    logger.exception("")
    press_enter("Press Enter to continue...")


class RestartException(BaseException):
    """Raise to restart the program without telling error to user"""
