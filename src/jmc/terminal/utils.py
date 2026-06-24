from enum import Enum
from getpass import getpass
import sys
from threading import Event
from traceback import format_exc
from ..compile import Logger

logger = Logger(__name__)


class Colors(Enum):
    HEADER = "\033[1;33m"
    YELLOW = "\033[33m"
    INFO = "\033[94m"
    INPUT = "\033[96m"
    PURPLE = "\033[35m"
    FAIL = "\033[91m"
    FAIL_BOLD = "\033[1;91m"
    ENDC = "\033[0m"
    EXIT = "\033[0m"
    NONE = "\033[0m"


def pprint(values, color: Colors = Colors.NONE, file=sys.stdout):
    """
    Print colored text

    :param values: Output text
    :param color: Output color (defaults to no color)
    :param file: Where to print (defaults to stdout)
    """
    if file.isatty():
        print(f"{color.value}{values}{Colors.ENDC.value}", file=file)
    else:
        print(values, file=file)


def eprint(values, color: Colors = Colors.FAIL):
    """
    Print error message to stderr

    :param values: Error text
    :param color: Error color (defaults to Colors.FAIL)
    """
    pprint(values, color, file=sys.stderr)


def get_input(prompt: str = "> ", color: Colors = Colors.INPUT) -> str:
    """
    Get an input from user

    :param prompt: Display string infront
    :param color: Color of the input and promt
    :return: input from user
    """
    if sys.stdout.isatty():
        input_value = input(f"{color.value}{prompt}")
        print(Colors.ENDC.value, end="", flush=True)
    else:
        input_value = input(prompt)
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
    eprint(type(error).__name__, Colors.FAIL_BOLD)
    eprint(error)


def handle_exception(error: Exception, event: Event, is_ok: bool):
    event.set()
    eprint("An unexpected error caused the program to crash")
    eprint(type(error).__name__, Colors.FAIL_BOLD)
    eprint(error)
    if not is_ok:
        eprint(format_exc(), Colors.YELLOW)
        eprint(
            "Please report this error at https://github.com/WingedSeal/jmc/issues/new/choose or https://discord.gg/PNWKpwdzD3.")
    logger.critical("Program crashed")
    logger.exception("")
    press_enter("Press Enter to continue...")


class RestartException(BaseException):
    """Raise to restart the program without telling error to user"""
