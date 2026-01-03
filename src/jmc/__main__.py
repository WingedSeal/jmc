"""Main module"""

import atexit
from enum import Enum, auto
import shutil
import subprocess
import argparse
import importlib.util
from pathlib import Path
import sys


from .terminal.configuration import Configuration
from .compile import Logger
from .terminal.utils import RestartException, handle_exception
from .terminal import GlobalData, Colors, start
from .config import VERSION, CONFIG_FILE_NAME

GlobalData().init(VERSION, CONFIG_FILE_NAME)
global_data: GlobalData = GlobalData()

from . import terminal_commands  # noqa

logger = Logger(__name__)

PACKAGE_NAME = "jmcfunction"
PACKAGE_SOURCE = "git+https://github.com/WingedSeal/jmc.git#subdirectory=src"


def main():
    """Main function"""
    logger.info(f"Argv: {sys.argv}")
    args = get_args()
    logger.info(f"Args: {args}")
    if args.command == "init":
        init(args)
    elif args.command == "compile":
        compile(args)
    elif args.command == "config":
        config(args)
    elif args.command == "run" or args.command is None:
        atexit.register(lambda: print(Colors.EXIT.value + "\n"))
        run()
    elif args.command == "update":
        update(args)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Javascript-like Minecraft Function")
    parser.add_argument("--version", "-v", action="version", version=VERSION)
    subparser = parser.add_subparsers(dest="command", required=False)

    compile_parser = subparser.add_parser("compile", help="compile")
    compile_parser.add_argument(
        "--environment",
        "--environments",
        "--env",
        "--envs",
        "-e",
        required=False,
        default=[],
        nargs="+",
        type=str,
        help="set macros defined with #env to 1",
    )

    run_parser = subparser.add_parser("run", help="start a jmc session")

    init_parser = subparser.add_parser("init", help="initialize configurations")
    init_parser.add_argument("--namespace", "-n", required=True, type=str)
    init_parser.add_argument(
        "--description", "--desc", "-d", default="", required=False, type=str
    )
    init_parser.add_argument(
        "--packformat", "--pack_format", "-p", required=True, type=int
    )
    init_parser.add_argument(
        "--target", "--target_path", "-t", required=False, type=Path
    )
    init_parser.add_argument(
        "--output", "--output_path", "-o", required=False, type=Path
    )
    init_parser.add_argument("--force", dest="is_force", action="store_true")

    config_parser = subparser.add_parser("config", help="edit configuration")
    config_parser.add_argument(
        "--config",
        "-c",
        required=True,
        type=str,
        choices=("namespace", "description", "pack_format", "target", "output"),
    )
    config_parser.add_argument("--value", "-v", required=True, type=str)

    update_parser = subparser.add_parser("update", help="update jmc from pip")
    update_parser.add_argument(
        "--git",
        "-g",
        dest="is_git",
        action="store_true",
        help="force install git version from github repository",
    )
    update_parser.add_argument(
        "--verbose",
        "-v",
        dest="is_verbose",
        action="store_true",
        help="show pip output",
    )

    args = parser.parse_args()
    return args


def init(args: argparse.Namespace):

    configuration = Configuration(
        global_data,
        args.namespace,
        args.description,
        args.packformat,
        args.target,
        args.output,
    )
    if args.target is None:
        configuration.target = configuration._default_target()
    if args.output is None:
        configuration.output = configuration._default_output()
    if not args.is_force and configuration.is_file_exist():
        print(
            "Initialization failed: Configuration file already exists. Run with `--force` to override the old file."
        )
        return
    configuration.save_config()


class Updater(Enum):
    PIP = auto()
    UV = auto()


def update(args: argparse.Namespace):
    """Update the CLI package to the latest version via pip"""
    git_version_detected = VERSION.endswith("-git")
    if git_version_detected:
        print("Git version detected")
        if args.is_git:
            print("Ignoring '--git' flag")
    elif args.is_git:
        print("Forcing git version")
    is_git = args.is_git or git_version_detected
    updater = _get_updater()
    if updater == Updater.PIP:
        if is_git:
            package = [
                "--force-reinstall",
                "--user",
                PACKAGE_SOURCE,
            ]
        else:
            package = [PACKAGE_NAME]
        command = (
            [sys.executable, "-m", "pip", "install", "--upgrade"]
            + (
                []
                if args.is_verbose
                else [
                    "--quiet",
                    "--quiet",
                ]  # It can be used up to 3 times (https://pip.pypa.io/en/stable/cli/pip/#cmdoption-q)
            )
            + package
        )
    elif updater == Updater.UV:
        command = ["uv", "tool", "upgrade", PACKAGE_SOURCE if is_git else PACKAGE_NAME]
    else:
        raise Exception("Unreachable")

    try:
        subprocess.check_call(command)
        print("Update installed")
    except subprocess.CalledProcessError as e:
        print(f"Update failed: {e}")
        sys.exit(1)


def _get_updater() -> Updater:
    if importlib.util.find_spec("pip") is not None:
        print("Module 'pip' found, updating...")
        return Updater.PIP
    print("Module 'pip' not found, falling back to 'uv' command")
    if shutil.which("uv") is not None:
        print("command 'uv' found")
        try:
            result = subprocess.run(
                ["uv", "tool", "list"], capture_output=True, text=True, check=True
            )
            if PACKAGE_NAME in result.stdout:
                print(f"'{PACKAGE_NAME}' package found in 'uv', updating...")
                return Updater.UV
        except subprocess.CalledProcessError:
            pass
        print(f"'{PACKAGE_NAME}' package not found in 'uv'")
    print("Update failed")
    sys.exit(1)


def config(args: argparse.Namespace):
    configuration = global_data.config
    configuration.load_config()
    if not configuration.is_file_exist():
        print("Configuration editing failed: Configuration file does not exists.")
        return
    setattr(configuration, args.config, args.value)
    configuration.save_config()


def compile(args: argparse.Namespace):
    if not global_data.config.is_file_exist():
        print("Compilation failed: Configuration file does not exists.")
    global_data.config.load_config()
    terminal_commands.compile_(*args.environment)


def run():
    logger.info("Starting session")
    while True:
        try:
            start()
        except Exception as error:
            handle_exception(error, global_data.EVENT, is_ok=True)
        except RestartException:
            pass
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
