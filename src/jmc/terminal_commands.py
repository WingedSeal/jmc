from datetime import datetime
import sys
from time import perf_counter
from traceback import format_exc

from .terminal.utils import error_report, handle_exception
from .terminal import pprint, Colors, GlobalData, add_command
from .compile import compile, Logger, EXCEPTIONS, get_debug_log

global_data = GlobalData()
logger = Logger(__name__)


@add_command("help [<command>]")
def help(command: str = "") -> None:
    """Output this message or get help for a command"""
    if not command:
        avaliable_commands = "\n".join(f"{usage}: {func.__doc__}" for _,
                                       (func, usage) in global_data.commands.items())
        pprint(f"""Avaliable commands:

{avaliable_commands}
""", color=Colors.YELLOW)
        return


@add_command("exit")
def exit():
    sys.exit(0)


@add_command("compile [debug]", "compile")
def compile_(debug: str = ""):
    if debug:
        if debug != 'debug':
            pprint("Did you mean: 'compile debug'")
            return
        pprint("DEBUG MODE", Colors.INFO)
    debug_compile = bool(debug)

    pprint("Compiling...", Colors.INFO)
    try:
        start_time = perf_counter()
        compile(global_data.config, debug=True)
        stop_time = perf_counter()
        pprint(
            f"Compiled successfully in {stop_time-start_time} seconds", Colors.INFO)
    except EXCEPTIONS as error:
        logger.debug(format_exc())
        error_report(error)
    except Exception as error:
        logger.exception("Non-JMC Error occur")
        # error_report(error)
        handle_exception(error, global_data.EVENT, is_ok=False)

    if debug_compile:
        __log_debug()
        __log_info()


def __log_debug():
    logger.info("Requesting debug log")
    global_data.LOG_PATH.mkdir(exist_ok=True)
    debug_log = get_debug_log()
    with (global_data.LOG_PATH / datetime.now().strftime("JMC_DEBUG - %y-%m-%d %H.%M.%S.log")).open('w+') as file:
        file.write(debug_log)
    with (global_data.LOG_PATH / "latest.log").open('w+') as file:
        file.write(debug_log)


def __log_info():
    logger.info("Requesting info log")
    global_data.LOG_PATH.mkdir(exist_ok=True)
    info_log = compile.get_info_log()
    with (global_data.LOG_PATH / datetime.now().strftime("JMC_INFO - %y-%m-%d %H.%M.%S.log")).open('w+') as file:
        file.write(info_log)
    with (global_data.LOG_PATH / "latest.log").open('w+') as file:
        file.write(info_log)
