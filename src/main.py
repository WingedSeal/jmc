import os
import atexit
import threading
from pathlib import Path
from enum import Enum
from json import dump, load
from datetime import datetime
from time import perf_counter
from getpass import getpass
from traceback import format_exc
from sys import exit

import jmc
from jmc.exception import (
    JMCDecodeJSONError,
    JMCFileNotFoundError,
    JMCSyntaxException,
    JMCSyntaxWarning,
    MinecraftSyntaxWarning,
    JMCBuildError
)

VERSION = 'v1.2.0-alpha'

CWD = Path(os.getcwd())
LOG_PATH = CWD / 'log'
CONFIG_FILE_NAME = 'jmc_config.json'
NEW_LINE = '\n'
config = {}

logger = jmc.Logger(__name__)


class Colors(Enum):
    HEADER = '\033[1;33;40m'
    YELLOW = '\033[33;40m'
    INFO = '\033[94;40m'
    INPUT = '\033[96;40m'
    PURPLE = '\033[35;40m'
    FAIL = '\033[91;40m'
    FAIL_BOLD = '\033[1;91;40m'
    ENDC = '\033[0;0;40m'
    EXIT = '\033[0;0;0m'
    NONE = '\033[0;37;40m'


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


def main() -> None:
    global config
    os.system("")
    logger.info(f"Build-version: {VERSION}")
    pprint(' JMC Compiler\n', Colors.HEADER)
    pprint(f'Current Directory | {CWD}\n', Colors.YELLOW)
    if not (CWD / CONFIG_FILE_NAME).is_file():
        pprint(
            f'No confile file found, generating {CONFIG_FILE_NAME}...', Colors.INFO
        )
        while True:
            config["namespace"] = get_input("Namespace: ")
            if " " in config["namespace"] or "\t" in config["namespace"]:
                pprint("Invalid Namespace: Space detected.", Colors.FAIL)
                continue
            if config["namespace"] == "":
                pprint(
                    "Invalid Namespace: Namespace need to have 1 or more character.", Colors.FAIL
                )
                continue
            if not config["namespace"].islower():
                pprint(
                    "Invalid Namespace: Uppercase character detected.",
                    Colors.FAIL)
                continue
            break
        config["description"] = get_input("Description: ")
        while True:
            config["pack_format"] = get_input("Pack Format: ")
            if not config["pack_format"].isdigit():
                pprint(
                    "Invalid Pack Format: Non integer detected.",
                    Colors.FAIL)
                continue
            break

        while True:
            config["target"] = get_input(
                f"Main JMC file(Leave blank for default[main.jmc]): "
            )
            if config["target"] == "":
                config["target"] = (
                    CWD / 'main.jmc'
                ).resolve().as_posix()
                break
            if not config["target"].endswith(".jmc"):
                pprint(
                    "Invalid path: Target file needs to end with .jmc",
                    Colors.FAIL)
                continue
            try:
                config["target"] = Path(config["target"]).resolve().as_posix()
            except BaseException:
                pprint("Invalid path", Colors.FAIL)
                continue
            break
        Path(config["target"]).touch(exist_ok=True)

        while True:
            config["output"] = get_input(
                "Output directory(Leave blank for default[current directory]): "
            )
            if config["output"] == "":
                config["output"] = CWD.resolve().as_posix()
                break
            try:
                output = Path(config["output"]).resolve()
                if output.is_file():
                    pprint("Path is not a directory.", Colors.FAIL)
                config["output"] = output.as_posix()
            except BaseException:
                pprint("Invalid path", Colors.FAIL)
                continue
            break

        with (CWD / CONFIG_FILE_NAME).open('w') as file:
            dump(config, file, indent=2)
    else:
        with (CWD / CONFIG_FILE_NAME).open('r') as file:
            config = load(file)
    pprint("To compile, type `compile`. For help, type `help`", Colors.INFO)
    while True:
        command = get_input().split()
        if not command:
            continue
        {
            "cd": CMD.cd,
            "help": CMD.help,
            "exit": CMD.exit,
            "compile": CMD.compile,
            "log": CMD.log,
            "autocompile": CMD.autocompile,
            "config": CMD.config,
        }.get(command[0], CMD.default)(*command[1:])


class CMD:
    event = threading.Event()

    @classmethod
    def default(cls, *arg):
        pprint("Command not recognized, try `help` for more info.", Colors.FAIL)

    @classmethod
    def help(cls, *arg):
        pprint("""Avaliable commands:

cd <path>: Change current directory
compile: Compile your JMC file(s)
autocompile <interval (second)>: Start automatically compiling with certain interval
log (debug|info): Create log file in output directory
log clear: Delete every log file inside log folder except latest
config reset: Delete the configuration file and restart the compiler
config edit: Override configuration file and bypass error checking
help: Output this message
exit: Exit compiler
""", color=Colors.YELLOW)

    @classmethod
    def cd(cls, *args):
        if not args:
            pprint("Usage: cd <path>", Colors.FAIL)
            return
        path = ' '.join(args)
        try:
            os.chdir(path)
            global CWD
            global LOG_PATH
            CWD = Path(os.getcwd())
            LOG_PATH = CWD / 'log'
            main()
        except ValueError:
            pprint("Invalid path", Colors.FAIL)

    @classmethod
    def exit(cls, *args):
        exit(0)

    @classmethod
    def compile(cls, *args):
        debug_compile = False
        if args:
            if len(args) == 1 and args[0] == 'debug':
                debug_compile = True
                pprint("DEBUG MODE", Colors.INFO)
            else:
                pprint("Usage: compile", Colors.FAIL)
                return
        pprint("Compiling...", Colors.INFO)
        try:
            start_time = perf_counter()
            jmc.compile(config, debug=True)
            stop_time = perf_counter()
            pprint(
                f"Compiled successfully in {stop_time-start_time} seconds", Colors.INFO)
        except (
            JMCSyntaxException,
            JMCFileNotFoundError,
            JMCDecodeJSONError,
            JMCSyntaxWarning,
            MinecraftSyntaxWarning,
            JMCBuildError
        ) as error:
            logger.debug(format_exc())
            error_report(error)
        except Exception as error:
            logger.exception("Non-JMC Error occur")
            error_report(error)

        if debug_compile:
            cls._log_debug()
            cls._log_clear()

    @classmethod
    def autocompile(cls, *args):
        if len(args) > 1 or len(args) == 0:
            pprint("Usage: autocompile <interval (second)>", Colors.FAIL)
            return
        try:
            interval = int(args[0])
        except ValueError:
            pprint("Invalid integer", Colors.FAIL)
            return
        except BaseException as error:
            pprint(type(error).__name__, Colors.FAIL_BOLD)
            pprint(error, Colors.FAIL)
        if interval == 0:
            pprint("Interaval cannot be 0 seconds", Colors.FAIL)
            return

        thread = threading.Thread(
            target=lambda: cls._background(interval),
            daemon=True
        )
        cls.event.clear()
        thread.start()

        press_enter("Press Enter to stop...\n")
        pprint("Stopping...", Colors.INFO)
        cls.event.set()
        thread.join()

    @classmethod
    def _background(cls, interval: int):
        while not cls.event.is_set():
            logger.debug("Auto compiling")
            cls.compile()
            cls.event.wait(interval)

    @classmethod
    def config(cls, *args):
        if not args:
            pprint("Usage: config (reset|edit)", Colors.FAIL)
            return
        if args[0] == 'reset':
            cls._config_reset()
        elif args[0] == 'edit':
            cls._config_reset()
        else:
            pprint("Usage: config (reset|edit)", Colors.FAIL)
            return

    @classmethod
    def _config_reset(cls):
        (CWD / CONFIG_FILE_NAME).unlink(missing_ok=True)
        pprint("Resetting configurations", Colors.PURPLE)
        print('\n' * 5)
        main()

    @classmethod
    def _config_edit(cls):
        global config
        pprint(f"""Edit configurations (Bypass error checking)
Type `cancel` to cancel
{NEW_LINE.join([f"- {key}" for key in config])}""", Colors.PURPLE)
        key = get_input("Configuration: ")
        if key not in config:
            if key.lower() == 'cancel':
                return
            pprint("Invalid Key", Colors.FAIL)
            cls._config_edit()
        else:
            pprint(f"Current {key}: {config[key]}", Colors.YELLOW)
            config[key] = get_input("New Value: ")
            with (CWD / CONFIG_FILE_NAME).open('w') as file:
                dump(config, file, indent=2)

    @classmethod
    def log(cls, *args):
        if len(args) > 1 or not args:
            pprint("Usage: log (debug|info|clear)", Colors.FAIL)
            return
        if args[0] == 'debug':
            cls._log_debug()
        elif args[0] == 'info':
            cls._log_info()
        elif args[0] == 'clear':
            cls._log_clear()
        else:
            pprint("Usage: log (debug|info|clear)", Colors.FAIL)
            return

    @classmethod
    def _log_clear(cls):
        logger.info("Clearing logs")
        if not LOG_PATH.is_dir():
            logger.debug("Log folder not found")
            return

        for path in LOG_PATH.iterdir():
            if not path.is_file():
                continue
            if path.suffix != '.log':
                continue
            if path.name == 'latest.log':
                continue
            path.unlink()

    @classmethod
    def _log_debug(cls):
        logger.info("Requesting debug log")
        LOG_PATH.mkdir(exist_ok=True)
        debug_log = jmc.get_debug_log()
        with (LOG_PATH / datetime.now().strftime("JMC_DEBUG - %y-%m-%d %H.%M.%S.log")).open('w+') as file:
            file.write(debug_log)
        with (LOG_PATH / "latest.log").open('w+') as file:
            file.write(debug_log)

    @classmethod
    def _log_info(cls):
        logger.info("Requesting info log")
        LOG_PATH.mkdir(exist_ok=True)
        info_log = jmc.get_info_log()
        with (LOG_PATH / datetime.now().strftime("JMC_INFO - %y-%m-%d %H.%M.%S.log")).open('w+') as file:
            file.write(info_log)
        with (LOG_PATH / "latest.log").open('w+') as file:
            file.write(info_log)


def handle_exception(error: Exception):
    """
    Tell user when unexpected crash happens and reset

    :param error: Exception
    """
    CMD.event.set()
    pprint("Unexpected error causes program to crash", Colors.FAIL)
    pprint(type(error).__name__, Colors.FAIL_BOLD)
    pprint(error, Colors.FAIL)
    pprint("NOTE: This shouldn't happen. Please contact WingedSeal.", Colors.FAIL)
    logger.critical("Program crashed")
    logger.exception("")
    press_enter("Press Enter to continue...")


if __name__ == '__main__':
    atexit.register(lambda: print(Colors.EXIT.value, end=""))
    logger.info("Starting session")
    while True:
        try:
            main()
        except Exception as error:
            handle_exception(error)
