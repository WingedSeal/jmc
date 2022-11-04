import sys
from .terminal import add_command
from .terminal import pprint, Colors, GlobalData


@add_command("help [<command>]")
def help(command: str | None = None) -> None:
    if command is None:
        pprint("""Avaliable commands:

cd <path>: Change current directory
compile: Compile your JMC file(s)
autocompile <interval (second)>: Start automatically compiling with certain interval
log (debug|info): Create log file in output directory
log clear: Delete every log file inside log folder except latest
config reset: Delete the configuration file and restart the compiler
config edit: Override configuration file and bypass error checking
version: Check JMC's version
help: Output this message
exit: Exit compiler
""", color=Colors.YELLOW)
        return


@add_command("exit")
def exit():
    sys.exit(0)
