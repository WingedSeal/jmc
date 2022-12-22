"""Main module"""
import atexit
from .compile import Logger
from .terminal.utils import RestartException, handle_exception
from .terminal import GlobalData, Colors, start

VERSION = 'v1.2.9'
CONFIG_FILE_NAME = 'jmc_config.json'
GlobalData().init(VERSION, CONFIG_FILE_NAME)

from . import terminal_commands  # noqa

logger = Logger(__name__)


def main():
    """Main function"""
    atexit.register(lambda: print(Colors.EXIT.value))
    logger.info("Starting session")
    global_data = GlobalData()
    while True:
        try:
            start()
        except Exception as error:
            handle_exception(error, global_data.EVENT, is_ok=True)
        except RestartException:
            pass
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
