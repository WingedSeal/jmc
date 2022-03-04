import os
import sys
import atexit
from pathlib import Path
from enum import Enum
from json import dump, load

CWD = Path(sys.argv[0]).parent
CONFIG_FILE_NAME = 'jmc_config.json'
NEW_LINE = '\n'
config = dict()


class Colors(Enum):
    HEADER = '\033[1;33;40m'
    YELLOW = '\033[33;40m'
    INFO = '\033[94;40m'
    INPUT = '\033[96;40m'
    PURPLE = '\033[35;40m'
    FAIL = '\033[91;40m'
    ENDC = '\033[0;0;40m'
    EXIT = '\033[0;0;0m'
    NONE = '\033[0;37;40m'


def pprint(values, color: Colors = Colors.NONE):
    print(f"{color.value}{values}{Colors.ENDC.value}")


def get_input(prompt: str = "> ", color: Colors = Colors.INPUT) -> str:
    input_value = input(f"{color.value}{prompt}")
    print(Colors.ENDC.value, end="")
    return input_value


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
                config["target"] = Path(config["target"])
                if not config["target"].is_absolute():
                    config["target"] = CWD/config["target"]
            except BaseException:
                pprint("Invalid path", Colors.FAIL)
                continue
            break

        while True:
            config["output"] = get_input(
                f"Output directory(Leave blank for default[current directory]): "
            )
            if config["output"] == "":
                config["output"] = (
                    CWD
                ).resolve().as_posix()
                break
            try:
                config["output"] = Path(config["output"])
                if not config["output"].is_absolute():
                    config["output"] = CWD/config["output"]
                if config["output"].is_file:
                    pprint("Path is not a directory.", Colors.FAIL)
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
            "autocompile": CMD.autocompile,
            "autocompile stop": CMD.autocompile_stop,
            "config reset": CMD.config_reset,
            "config edit": CMD.config_edit
        }.get(get_input(), CMD.default)()


class CMD:
    @classmethod
    def default(cls):
        pprint("Command not regonized, try `help` for more info.", Colors.FAIL)

    @classmethod
    def help(cls):
        pprint("""Avaliable commands:

compile: Compile your JMC file(s)
autocompile: Make compiler compile automatically after certain period
autocompile stop: Stop auto-compiling
config reset: Delete the configuration file and restart the compiler
config edit: Override configuration file and bypass error checking
exit: Exit compiler
""", color=Colors.YELLOW)

    @classmethod
    def exit(cls):
        exit(0)

    @classmethod
    def compile(cls):
        print("TEST")

    @classmethod
    def autocompile(cls):
        print("TEST_AUTO")

    @classmethod
    def autocompile_stop(cls):
        print("TEST_AUTO_STOP")

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


if __name__ == '__main__':
    atexit.register(lambda: print(Colors.EXIT.value, end=""))
    main()
