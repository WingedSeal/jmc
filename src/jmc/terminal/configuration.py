import functools
from json import JSONDecodeError, dump, load
import os
from pathlib import Path
import threading
from typing import Any, Callable, Protocol

from .utils import Colors, get_input, pprint
from ..compile.utils import SingleTon
from ..compile import Logger
from dataclasses import dataclass

logger = Logger(__name__)


# class TerminalCommand(Protocol):
#     """Protocal for a function(callable) representing a jmc terminal command"""
#     __name__: str

#     def __call__(self, *args: str) -> None:
#         ...
TerminalCommand = Callable[..., None]


@dataclass(slots=True, frozen=True, order=True, eq=True)
class MinecraftVersion:
    major: int
    minor: int
    patch: int = 0

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}'


PACK_VERSION = {
    MinecraftVersion(1, 20, 2): "18",
    MinecraftVersion(1, 20): "15",
    MinecraftVersion(1, 19, 4): "12",
    MinecraftVersion(1, 19): "10",
    MinecraftVersion(1, 18, 2): "9",
    MinecraftVersion(1, 18): "8",
    MinecraftVersion(1, 17): "7",
    MinecraftVersion(1, 16, 2): "6",
    MinecraftVersion(1, 15): "5",
    MinecraftVersion(1, 13): "4"
}
"""Dictionary of MinecraftVersion and it's coresponding pack_format"""


def get_pack_format(string: str) -> str:
    """
    Convert string of pack_format or minecraft's version
    - Return empty string if input is invalid

    :param string: Input string
    :return: pack_format if valid, else empty string
    """
    if "." not in string:
        if not string.isdigit():
            pprint(
                "Invalid Pack Format: Non integer detected.",
                Colors.FAIL)
            return ""
        return string

    string_split = string.split(".")
    if not 2 <= len(string_split) <= 3:
        pprint(
            f"Invalid Minecraft version: Expect 1 or 2 dot (got {len(string_split)-1}).",
            Colors.FAIL)
        return ""

    try:
        current_version = MinecraftVersion(*(int(x) for x in string_split))
    except ValueError:
        pprint(
            "Invalid Minecraft version: Non integer detected.",
            Colors.FAIL)
        return ""

    for minecraft_version, pack_format in PACK_VERSION.items():
        if current_version > minecraft_version:
            return pack_format

    pprint(
        f"Invalid Minecraft version: Version {current_version} does not support datapack.",
        Colors.FAIL)
    return ""


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
    is_configed: bool = False

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
        if self.target.is_relative_to(self.global_data.cwd):
            target = self.target.relative_to(self.global_data.cwd)
        else:
            target = self.target
        if self.output.is_relative_to(self.global_data.cwd):
            output = self.output.relative_to(self.global_data.cwd)
        else:
            output = self.output
        return {
            "namespace": self.namespace,
            "description": self.description,
            "pack_format": self.pack_format,
            "target": target.as_posix(),
            "output": output.as_posix(),
        }

    def load_config(self) -> None:
        """
        Read configuration file
        """
        try:
            with (self.global_data.cwd / self.global_data.CONFIG_FILE_NAME).open("r", encoding="utf-8") as file:
                json = load(file)
            self.namespace = json["namespace"]
            self.description = json["description"]
            self.pack_format = json["pack_format"]
            self.target = self.global_data.cwd / json["target"]
            self.output = self.global_data.cwd / json["output"]
            self.is_configed = True
        except JSONDecodeError as error:
            pprint(
                f"Invalid JSON syntax in {self.global_data.CONFIG_FILE_NAME}. Delete the file to reset the configuration.", Colors.FAIL
            )
            raise error from error
        except KeyError as error:
            pprint(
                f"Invalid JSON data in {self.global_data.CONFIG_FILE_NAME}. Delete the file to reset the configuration.", Colors.FAIL
            )
            raise error from error

    def save_config(self):
        """
        Save configuration to file
        """
        pprint(
            f"Your configuration has been saved to {self.global_data.CONFIG_FILE_NAME}", Colors.INFO
        )
        with (self.global_data.cwd / self.global_data.CONFIG_FILE_NAME).open("w", encoding="utf-8") as file:
            dump(self.toJSON(), file, indent=4)

    def ask_and_save(self):
        """
        Ask for configuration from user(tell user that configuration is not set), and if user successfully finish the configuration, save it
        """
        pprint(
            f"No config file found, generating {self.global_data.CONFIG_FILE_NAME}...", Colors.INFO
        )
        self.ask_config()
        if self.is_configed:
            self.save_config()

    def ask_config(self):
        """
        Ask for configuration from user
        """
        # Namespace
        while True:
            namespace = get_input("Namespace(Leave blank to cancel): ")
            if " " in namespace or "\t" in namespace:
                pprint("Invalid Namespace: Space detected.", Colors.FAIL)
                continue
            if namespace == "":
                pprint(
                    f"Configuration canceled.{' Using backup configuration.' if self.is_configed else ''}", Colors.FAIL
                )
                return
            if not namespace.islower():
                pprint(
                    "Invalid Namespace: Uppercase character detected.",
                    Colors.FAIL)
                continue
            break
        self.namespace = namespace
        self.is_configed = True

        # Description
        self.description = get_input("Description: ")

        # Pack Format
        while True:
            pack_format = get_pack_format(
                get_input("Pack Format or Minecraft version: "))
            if not pack_format:
                continue
            break
        self.pack_format = pack_format

        # Target
        while True:
            target_str = get_input(
                "Main JMC file(Leave blank for default[main.jmc]): "
            )
            if target_str == "":
                target = self._default_target()
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
                output = self._default_output()
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

    def _default_output(self):
        return self.global_data.cwd.resolve()

    def _default_target(self):
        return (self.global_data.cwd / "main.jmc").resolve()

    def __bool__(self) -> bool:
        return self.is_configed

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
        "config",
        "cwd",
        "VERSION",
        "CONFIG_FILE_NAME",
        "LOG_PATH",
        "EVENT",
        "commands")

    def init(self, version: str, config_file_name: str) -> None:
        self.config = Configuration(self)
        self.cwd: Path = Path(os.getcwd())
        self.VERSION: str = version
        self.CONFIG_FILE_NAME: str = config_file_name
        self.LOG_PATH = self.cwd / "log"
        self.commands: dict[str, tuple[TerminalCommand, str]] = {}
        """Dictionary of command_name and tuple of function and its usage(string)"""
        self.EVENT = threading.Event()
        self.interval = -1

    def add_command(self, func: TerminalCommand, usage: str) -> None:
        command = func.__name__
        if command in self.commands:
            raise ValueError("Duplicated terminal command")
        self.commands[command] = (func, usage)


def add_command(
        usage: str, rename: str = ""):
    """
    Decorator factory to add terminal command

    :param func: Function for decorator
    :return: decorator function
    """
    def decorator(func: TerminalCommand) -> TerminalCommand:
        """
        Decorator to add terminal command

        :param func: Function for decorator
        :return: the same function
        """
        logger.debug(
            f"Terminal command added: {func.__name__}{' as'+rename if rename else ''}")
        if rename:
            func.__name__ = rename
        GlobalData().add_command(func, usage)

        return func
    return decorator
