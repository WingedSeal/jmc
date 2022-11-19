import functools
from json import JSONDecodeError, dump, load
import os
from pathlib import Path
import threading
from typing import Any, Callable

from .utils import Colors, get_input, pprint
from ..compile.utils import SingleTon
from ..compile import Logger
from dataclasses import dataclass

logger = Logger(__name__)


@dataclass(slots=True)
class Configuration:
    """
    SingleTon storing all configuration data.
    """
    global_data: "GlobalData"
    namespace: str = ""
    description: str = ""
    pack_format: str = ""
    target: Path = Path()
    output: Path = Path()

    @property
    def target_str(self) -> str:
        if self.target is None:
            raise ValueError("Configuration not initialized")
        return self.target.absolute().as_posix()

    @property
    def output_str(self) -> str:
        if self.output is None:
            raise ValueError("Configuration not initialized")
        return self.output.absolute().as_posix()

    def toJSON(self) -> dict[str, Any]:
        """
        Turn get JSON from instance

        :return: JSON
        """
        # if not self.target or not self.output:
        #     raise ValueError("toJSON used on empty config")
        return {
            "namespace": self.namespace,
            "description": self.description,
            "pack_format": self.pack_format,
            "target": self.target.as_posix(),
            "output": self.output.as_posix(),
        }

    def load_config(self) -> None:
        """
        Read configuration file
        """
        try:
            with (self.global_data.cwd / self.global_data.CONFIG_FILE_NAME).open('r') as file:
                json = load(file)
            self.namespace = json["namespace"]
            self.description = json["description"]
            self.pack_format = json["pack_format"]
            self.target = Path(json["target"])
            self.output = Path(json["output"])
        except JSONDecodeError as error:
            pprint(
                f"Invalid JSON syntax in {self.global_data.CONFIG_FILE_NAME}. Delete the file to reset the configuration.", Colors.FAIL
            )
            raise error
        except KeyError as error:
            pprint(
                f"Invalid JSON data in {self.global_data.CONFIG_FILE_NAME}. Delete the file to reset the configuration.", Colors.FAIL
            )
            raise error

    def save_config(self):
        """
        Save configuration to file
        """
        with (self.global_data.cwd / self.global_data.CONFIG_FILE_NAME).open('w') as file:
            dump(self.toJSON(), file, indent=2)

    def ask_config(self):
        """
        Ask for configuration from user
        """
        # Namespace
        while True:
            namespace = get_input("Namespace: ")
            if " " in namespace or "\t" in namespace:
                pprint("Invalid Namespace: Space detected.", Colors.FAIL)
                continue
            if namespace == "":
                pprint(
                    "Invalid Namespace: Namespace need to have 1 or more character.", Colors.FAIL
                )
                continue
            if not namespace.islower():
                pprint(
                    "Invalid Namespace: Uppercase character detected.",
                    Colors.FAIL)
                continue
            break
        self.namespace = namespace

        # Description
        self.description = get_input("Description: ")

        # Pack Format
        while True:
            pack_format = get_input("Pack Format: ")
            if not pack_format.isdigit():
                pprint(
                    "Invalid Pack Format: Non integer detected.",
                    Colors.FAIL)
                continue
            break
        self.pack_format = pack_format

        # Target
        while True:
            target_str = get_input(
                f"Main JMC file(Leave blank for default[main.jmc]): "
            )
            if target_str == "":
                target = (
                    self.global_data.cwd / 'main.jmc'
                ).resolve()
                break
            if not target_str.endswith(".jmc"):
                pprint(
                    "Invalid path: Target file needs to end with .jmc",
                    Colors.FAIL)
                continue
            try:
                target = Path(target_str).resolve()
            except BaseException:
                pprint("Invalid path", Colors.FAIL)
                continue
            break
        target.touch(exist_ok=True)
        self.target = target

        # Output
        while True:
            output_str = get_input(
                "Output directory(Leave blank for default[current directory]): "
            )
            if output_str == "":
                output = self.global_data.cwd.resolve()
                break
            try:
                output = Path(output_str).resolve()
                if output.is_file():
                    pprint("Path is not a directory.", Colors.FAIL)
                    continue
            except BaseException:
                pprint("Invalid path", Colors.FAIL)
                continue
            break
        self.output = output

    @staticmethod
    def is_file_exist() -> bool:
        """
        Check whether configuration file exist

        :return: Whether configuration file exist
        """
        global_data = GlobalData()
        return (global_data.cwd / global_data.CONFIG_FILE_NAME).is_file()


class GlobalData(SingleTon):
    """
    SingleTon storing all data shared across all modules.
    """
    __slots__ = (
        'config',
        'cwd',
        'VERSION',
        'CONFIG_FILE_NAME',
        'LOG_PATH',
        'EVENT',
        'commands')

    def init(self, version: str, config_file_name: str) -> None:
        self.config = Configuration(self)
        self.cwd: Path = Path(os.getcwd())
        self.VERSION: str = version
        self.CONFIG_FILE_NAME: str = config_file_name
        self.LOG_PATH = self.cwd / 'log'
        self.commands: dict[str, tuple[Callable[..., Any], str]] = {}
        """Dictionary of command_name and tuple of function and its usage(string)"""
        self.EVENT = threading.Event()
        self.interval = -1

    def add_command(self, func: Callable[..., Any], usage: str) -> None:
        command = func.__name__
        if command in self.commands:
            raise ValueError("Duplicated terminal command")
        self.commands[command] = (func, usage)


def add_command(
        usage: str, rename: str = "") -> Callable[[Callable[..., None]], Callable[..., None]]:
    """
    Decorator factory to add terminal command

    :param func: Function for decorator
    :return: Wrapper function
    """
    def decorator(func: Callable[..., None]) -> Callable[..., None]:
        """
        Decorator to add terminal command

        :param func: Function for decorator
        :return: Wrapper function
        """
        logger.debug(
            f"Terminal command added: {func.__name__}{' as'+rename if rename else ''}")
        if rename:
            func.__name__ = rename
        GlobalData().add_command(func, usage)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
        return wrapper
    return decorator
