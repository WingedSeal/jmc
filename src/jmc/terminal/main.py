import os
from .configuration import GlobalData
from .utils import Colors, get_input, pprint
from ..compile import Logger

logger = Logger(__name__)

global_data: GlobalData = GlobalData()


def unknown_command(*args, **kwargs) -> None:
    pprint("Command not recognized, try `help` for more info.", Colors.FAIL)


def handle_command(given_command: str) -> None:
    if not given_command:
        return
    command_name, *arguments = given_command.split()
    command_func, usage = global_data.commands.get(
        command_name, (unknown_command, ""))
    try:
        command_func(*arguments)
    except TypeError as error:
        msg: str = error.args[0]
        msg = msg.replace(
            "()",
            " command").replace(
            "positional argument",
            "argument")
        pprint(msg, Colors.FAIL)
        pprint(f"Usage: {usage}", Colors.FAIL)


def start() -> None:
    os.system("")
    logger.info(f"Build-version: {global_data.VERSION}")
    pprint(f" JMC Compiler {global_data.VERSION}\n", Colors.HEADER)
    pprint(f"Current Directory | {global_data.cwd}\n", Colors.YELLOW)
    if not global_data.config.is_file_exist():
        global_data.config.ask_and_save()
    else:
        global_data.config.load_config()
    if global_data.config:
        pprint("To compile, type `compile`. For help, type `help`", Colors.INFO)
    else:
        pprint(
            "To setup workspace, type `config`. For help, type `help`",
            Colors.INFO)
    while True:
        handle_command(get_input())
