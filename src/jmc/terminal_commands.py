"""Contain all function representation of jmc terminal command"""
from datetime import datetime
from json import dump
import os
from pathlib import Path
import sys
import threading
from time import perf_counter
from traceback import format_exc

from .compile.header import Header

from .terminal.utils import RestartException, error_report, get_input, handle_exception, press_enter
from .terminal import pprint, Colors, GlobalData, add_command
from .compile import compile_jmc, Logger, EXCEPTIONS, get_debug_log, get_info_log

global_data: GlobalData = GlobalData()
logger = Logger(__name__)

NEW_LINE = "\n"


@add_command("help [<command>]", rename="help")
def help_(command: str = "") -> None:
    """Output this message or get help for a command"""
    if not command:
        avaliable_commands = "\n".join(f"- {usage}: {func.__doc__}" for _,
                                       (func, usage) in global_data.commands.items())
        pprint(f"""Avaliable commands:

{avaliable_commands}
""", color=Colors.YELLOW)
        return

    if command not in global_data.commands:
        raise TypeError(f"Unrecognized command '{command}'")
    func, usage = global_data.commands[command]
    pprint(f"{usage}: {func.__doc__}", Colors.YELLOW)


@add_command("exit", rename="exit")
def exit_() -> None:
    """Exit JMC compiler"""
    sys.exit(0)


@add_command("compile [debug]", "compile")
def compile_(debug: str = "") -> None:
    """Compile main JMC file"""
    if debug:
        if debug != "debug":
            raise TypeError(f"Unrecognized argument '{debug}'")
        pprint("DEBUG MODE", Colors.INFO)
    debug_compile = bool(debug)

    pprint("Compiling...", Colors.INFO)
    if not global_data.config:
        global_data.config.ask_and_save()
        return
    try:
        start_time = perf_counter()
        compile_jmc(global_data.config, debug=True)
        finished_compiled_time = Header().finished_compiled_time
        stop_time = perf_counter()
        pprint(
            f"Compiled successfully in {finished_compiled_time-start_time:.5f} seconds, datapack built in {stop_time-finished_compiled_time:.5f} seconds", Colors.INFO)
    except EXCEPTIONS as error:
        logger.debug(format_exc())
        error_report(error)
    except Exception as error:
        logger.exception("Non-JMC Error occur")
        handle_exception(error, global_data.EVENT, is_ok=False)

    if debug_compile:
        __log_debug()
        __log_info()


def __log_debug() -> None:
    logger.info("Requesting debug log")
    global_data.LOG_PATH.mkdir(exist_ok=True)
    debug_log = get_debug_log()
    with (global_data.LOG_PATH / datetime.now().strftime("JMC_DEBUG - %y-%m-%d %H.%M.%S.log")).open("w+", encoding="utf-8") as file:
        file.write(debug_log)
    with (global_data.LOG_PATH / "latest.log").open("w+", encoding="utf-8") as file:
        file.write(debug_log)


def __log_info() -> None:
    logger.info("Requesting info log")
    global_data.LOG_PATH.mkdir(exist_ok=True)
    info_log = get_info_log()
    with (global_data.LOG_PATH / datetime.now().strftime("JMC_INFO - %y-%m-%d %H.%M.%S.log")).open("w+", encoding="utf-8") as file:
        file.write(info_log)
    with (global_data.LOG_PATH / "latest.log").open("w+", encoding="utf-8") as file:
        file.write(info_log)


def __log_clear() -> None:
    logger.info("Clearing logs")
    if not global_data.LOG_PATH.is_dir():
        logger.debug("Log folder not found")
        return

    for path in global_data.LOG_PATH.iterdir():
        if not path.is_file():
            continue
        if path.suffix != ".log":
            continue
        if path.name == "latest.log":
            continue
        path.unlink()


@add_command("log debug|info|clear")
def log(mode: str) -> None:
    """
  - debug|info: Create log file in output directory
  - clear: Delete every log file inside log folder except latest"""
    if mode not in {"debug", "info", "clear"}:
        raise TypeError(f"Unrecognized mode '{mode}'")

    if mode == "debug":
        __log_debug()
    elif mode == "info":
        __log_info()
    elif mode == "clear":
        __log_clear()


@add_command("version")
def version() -> None:
    """Get JMC's version info"""
    pprint(global_data.VERSION, Colors.INFO)


def __config_reset() -> None:
    (global_data.cwd / global_data.CONFIG_FILE_NAME).unlink(missing_ok=True)
    pprint("Resetting configurations", Colors.PURPLE)
    print("\n" * 5)
    raise RestartException()


def __config_edit() -> None:
    config_json = global_data.config.toJSON()
    pprint(f"""Edit configurations (Bypass error checking)
Type `cancel` to cancel
{NEW_LINE.join([f"- {key}" for key in config_json])}""", Colors.PURPLE)
    key = get_input("Configuration: ").strip()
    if key not in config_json:
        if key.lower() == "cancel":
            return
        pprint("Invalid Key", Colors.FAIL)
        __config_edit()
    else:
        pprint(f"Current {key}: {config_json[key]}", Colors.YELLOW)
        config_json[key] = get_input("New Value: ")
        with (global_data.cwd / global_data.CONFIG_FILE_NAME).open("w", encoding="utf-8") as file:
            dump(config_json, file, indent=4)

        global_data.config.load_config()


@add_command("config [edit|reset]")
def config(mode: str = "") -> None:
    """Setup workspace's configuration
  - reset: Delete the configuration file and restart the compiler
  - edit: Override configuration file and bypass error checking"""
    if not mode:
        if not global_data.config:
            global_data.config.ask_and_save()
            return
        pprint(
            "Configuration file is already generated. To reset, use `cofig reset`",
            Colors.FAIL)
    if mode == "reset":
        __config_reset()
    elif mode == "edit":
        __config_edit()
    else:
        raise TypeError(f"Unrecognized mode '{mode}'")


def __background() -> None:
    while not global_data.EVENT.is_set():
        logger.debug("Auto compiling")
        compile_()
        global_data.EVENT.wait(global_data.interval)


@add_command("autocompile <interval (second)>")
def autocompile(interval: str) -> None:
    """Start automatically compiling with certain interval (Press Enter to stop)"""
    try:
        global_data.interval = int(interval)
    except ValueError as error:
        raise TypeError("Invalid integer for interval") from error
    if global_data.interval == 0:
        pprint("Interaval cannot be 0 seconds", Colors.FAIL)
        return

    if not global_data.config:
        global_data.config.ask_and_save()
        return

    thread = threading.Thread(
        target=__background,
        daemon=True
    )
    global_data.EVENT.clear()
    thread.start()

    press_enter("Press Enter to stop...\n")
    pprint("Stopping...", Colors.INFO)
    global_data.EVENT.set()
    thread.join()


@add_command("cd <path>", rename="cd")
def chdir(path: str) -> None:
    """Change current directory"""
    try:
        os.chdir(path)
    except (ValueError, FileNotFoundError):
        pprint("Invalid path", Colors.FAIL)
        return
    global_data.cwd = Path(os.getcwd())
    global_data.LOG_PATH = global_data.cwd / "log"
    raise RestartException
