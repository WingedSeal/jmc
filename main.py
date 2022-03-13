import os
import atexit
import threading
from pathlib import Path
from enum import Enum
from json import dump, load
from datetime import datetime
from time import perf_counter

import jmc
from jmc.exception import JMCDecodeJSONError, JMCFileNotFoundError, JMCSyntaxException, JMCSyntaxWarning

CWD = Path(os.getcwd())
LOG_PATH = CWD/'log'
CONFIG_FILE_NAME = 'jmc_config.json'
NEW_LINE = '\n'
config = dict()

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
    print(f"{color.value}{values}{Colors.ENDC.value}")


def get_input(prompt: str = "> ", color: Colors = Colors.INPUT) -> str:
    input_value = input(f"{color.value}{prompt}")
    print(Colors.ENDC.value, end="")
    logger.info(f"Input from user: {input_value}")
    return input_value


def error_report(error: Exception):
    pprint(type(error).__name__, Colors.FAIL_BOLD)
    pprint(error, Colors.FAIL)


def main() -> None:
    global config
    os.system("")
    pprint(' JMC Compiler\n', Colors.HEADER)
    if not (CWD/CONFIG_FILE_NAME).is_file():
        pprint(
            f'No confile file found, generating {CONFIG_FILE_NAME}...', Colors.INFO
        )
        while True:
            config["namespace"] = get_input(f"Namespace: ")
            if " " in config["namespace"] or "\t" in config["namespace"]:
                pprint("Invalid Namespace: Space detected.", Colors.FAIL)
                continue
            if config["namespace"] == "":
                pprint(
                    "Invalid Namespace: Namespace need to have 1 or more character.", Colors.FAIL
                )
                continue
            if not config["namespace"].islower():
                pprint("Invalid Namespace: Uppercase character detected.", Colors.FAIL)
                continue
            break
        config["description"] = get_input(f"Description: ")
        while True:
            config["pack_format"] = get_input(f"Pack Format: ")
            if not config["pack_format"].isdigit():
                pprint("Invalid Pack Format: Non integer detected.", Colors.FAIL)
                continue
            break

        while True:
            config["target"] = get_input(
                f"Main JMC file(Leave blank for default[main.jmc]): "
            )
            if config["target"] == "":
                config["target"] = (
                    CWD/'main.jmc'
                ).resolve().as_posix()
                break
            if not config["target"].endswith(".jmc"):
                pprint("Invalid path: Target file needs to end with .jmc", Colors.FAIL)
                continue
            try:
                config["target"] = Path(config["target"]).resolve().as_posix()
            except BaseException:
                pprint("Invalid path", Colors.FAIL)
                continue
            break

        while True:
            config["output"] = get_input(
                f"Output directory(Leave blank for default[current directory]): "
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

        with (CWD/CONFIG_FILE_NAME).open('w') as file:
            dump(config, file, indent=2)
    else:
        with (CWD/CONFIG_FILE_NAME).open('r') as file:
            config = load(file)
    pprint("To compile, type `compile`. For help, type `help`", Colors.INFO)
    while True:
        {
            "help": CMD.help,
            "exit": CMD.exit,
            "compile": CMD.compile,
            "log debug": CMD.log_debug,
            "log info": CMD.log_info,
            "autocompile": CMD.autocompile,
            "config reset": CMD.config_reset,
            "config edit": CMD.config_edit
        }.get(get_input(), CMD.default)()


class CMD:
    event = threading.Event()

    @classmethod
    def default(cls):
        pprint("Command not regonized, try `help` for more info.", Colors.FAIL)

    @classmethod
    def help(cls):
        pprint("""Avaliable commands:

compile: Compile your JMC file(s)
autocompile: Start automatically compiling with certain interval
log debug: Create log file in output directory
log info: Create log file in output directory
config reset: Delete the configuration file and restart the compiler
config edit: Override configuration file and bypass error checking
help: Output this message
exit: Exit compiler
""", color=Colors.YELLOW)

    @classmethod
    def exit(cls):
        exit(0)

    @classmethod
    def compile(cls):
        pprint("Compiling...", Colors.INFO)
        try:
            start_time = perf_counter()
            jmc.compile(config)
            stop_time = perf_counter()
            pprint(
                f"Compiled successfully in {stop_time-start_time} seconds", Colors.INFO)
        except (JMCSyntaxException, JMCFileNotFoundError, JMCDecodeJSONError, JMCSyntaxWarning) as error:
            error_report(error)
        except Exception as error:
            logger.exception("Non-JMC Exception occur")
            error_report(error)

    @classmethod
    def autocompile(cls):
        while True:
            try:
                interval = int(get_input("Interval(second): "))
                break
            except ValueError:
                pprint("Invalid integer", Colors.FAIL)
            except BaseException as error:
                pprint(type(error).__name__, Colors.FAIL_BOLD)
                pprint(error, Colors.FAIL)

        thread = threading.Thread(
            target=lambda: cls.background(interval),
            daemon=True
        )
        cls.event.clear()
        thread.start()

        get_input("Press Enter to stop...\n")
        pprint("Stopping...", Colors.INFO)
        cls.event.set()
        thread.join()

    @classmethod
    def background(cls, interval: int):
        while not cls.event.is_set():
            logger.debug("Auto compiling")
            cls.compile()
            cls.event.wait(interval)

    @classmethod
    def config_reset(cls):
        (CWD/CONFIG_FILE_NAME).unlink(missing_ok=True)
        pprint("Resetting configurations", Colors.PURPLE)
        print('\n'*5)
        main()

    @classmethod
    def config_edit(cls):
        global config
        pprint(f"""Edit configurations (Bypass error checking)
Type `cancel` to cancel
{NEW_LINE.join([f"- {key}" for key in config])}""", Colors.PURPLE)
        key = get_input("Configuration: ")
        if key not in config:
            if key.lower() == 'cancel':
                return
            pprint("Invalid Key", Colors.FAIL)
            cls.config_edit()
        else:
            pprint(f"Current {key}: {config[key]}", Colors.YELLOW)
            config[key] = get_input("New Value: ")
            with (CWD/CONFIG_FILE_NAME).open('w') as file:
                dump(config, file, indent=2)

    @classmethod
    def log_debug(cls):
        logger.info("Requesting debug log")
        LOG_PATH.mkdir(exist_ok=True)
        debug_log = jmc.get_debug_log()
        with (LOG_PATH/datetime.now().strftime("JMC_DEBUG - %y-%m-%d %H.%M.%S.log")).open('w+') as file:
            file.write(debug_log)
        with (LOG_PATH/"latest.log").open('w+') as file:
            file.write(debug_log)

    @classmethod
    def log_info(cls):
        logger.info("Requesting info log")
        LOG_PATH.mkdir(exist_ok=True)
        info_log = jmc.get_info_log()
        with (LOG_PATH/datetime.now().strftime("JMC_INFO - %y-%m-%d %H.%M.%S.log")).open('w+') as file:
            file.write(info_log)
        with (LOG_PATH/"latest.log").open('w+') as file:
            file.write(info_log)
        print()


if __name__ == '__main__':
    atexit.register(lambda: print(Colors.EXIT.value, end=""))
    logger.info("Starting session")
    while True:
        try:
            main()
        except Exception as error:
            pprint("Unexpected error causes program to crash", Colors.FAIL)
            pprint(type(error).__name__, Colors.FAIL_BOLD)
            pprint(error, Colors.FAIL)
            logger.critical("Program crashed")
            logger.exception("")
            get_input("Press Enter to continue... ")
