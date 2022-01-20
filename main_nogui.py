import traceback
import json
from pathlib import Path
from os import system
from sys import argv

from config import set_configs

CONFIG_FILE_NAME = 'jmc_config.json'
CONFIG_FILE = Path(argv[0]).parent/CONFIG_FILE_NAME
DEFAULT_CONFIG = {
    'namespace': 'default_namespace',
    'description': 'Compiled by JMC(Made by WingedSeal)',
    'pack_format': 7,
    'target': (Path(argv[0]).parent/'main.jmc').resolve().as_posix(),
    'output': Path(argv[0]).parent.resolve().as_posix(),
    'debug_mode': False
}


def main():
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open('r') as file:
                config = json.load(file)
                set_configs(config)

        except json.JSONDecodeError:
            print(
                f"JSONDecodeError, Your {CONFIG_FILE_NAME} might have invalid or malformed JSON.")
            print("To reset the config, simply delete the file and run again.")
            system("pause")
            return

        except BaseException as e:
            traceback.print_exc()
            print(
                f'\nEncounter unknown error when *parsing* {CONFIG_FILE_NAME}')
            system("pause")
            return

        try:
            from jmc import DataPack

            def compile() -> None:
                datapack = DataPack()
                datapack.init()
                datapack.compile()
            while True:
                compile()
                print(
                    f"\nSuccessfully compiled {config['target']} to {config['output']}")
                system("pause")
        except FileNotFoundError as e:
            traceback.print_exc()
            print(f'\nFile Missing')
            system("pause")
            return
        except BaseException:
            traceback.print_exc()
            print(f'\nEncounter unknown error when *compiling*')
            system("pause")
            return

    else:
        with CONFIG_FILE.open('w') as file:
            json.dump(DEFAULT_CONFIG, file, indent=2)
        print(f"Generated {CONFIG_FILE_NAME}")
        print(f"For documentation, https://wingedseal.github.io/docs.jmc/")
        print(f"Edit the configuration and run again.")
        system("pause")


if __name__ == '__main__':
    main()
