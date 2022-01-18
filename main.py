from os import system
import traceback
import json
from sys import argv
from pathlib import Path
from config import set_configs


FILE_NAME = 'jmc_config.json'


def main():
    config_file = Path(argv[0]).parent/FILE_NAME
    if config_file.exists():
        try:
            with config_file.open('r') as file:
                config = json.load(file)
                set_configs(config)

        except json.JSONDecodeError:
            print(
                f"JSONDecodeError, Your {FILE_NAME} might have invalid or malformed JSON.")
            print("To reset the config, simply delete the file and run again.")
            system("pause")
            return

        except BaseException as e:
            traceback.print_exc()
            print(f'\nEncounter unknown error when *parsing* {FILE_NAME}')
            system("pause")
            return

        try:
            from jmc import DataPack

            def compile() -> None:
                datapack = DataPack()
                datapack.init()
                datapack.compile()
            if config['keep_compiling']:
                while True:
                    compile()
                    print(
                        f"\nSuccessfully compiled {config['target']} to {config['output']}")
                    system("pause")
            else:
                compile()
                print(
                    f"\nSuccessfully compiled {config['target']} to {config['output']}")
                system("pause")
        except FileNotFoundError as e:
            traceback.print_exc()
            print(f'\nFile Missing')
            print(e)
            system("pause")
            return
        except BaseException:
            traceback.print_exc()
            print(f'\nEncounter unknown error when *compiling*')
            system("pause")
            return

    else:
        config = {
            'namespace': 'namespace',
            'description': 'Compiled by JMC(Made by WingedSeal)',
            'pack_format': 7,
            'target': (Path(argv[0]).parent/'main.jmc').resolve().as_posix(),
            'output': Path(argv[0]).parent.resolve().as_posix(),
            'keep_compiling': False,
            'debug_mode': False
        }
        with config_file.open('w') as file:
            json.dump(config, file, indent=2)
        print(f"Generated {FILE_NAME}")
        print(f"For documentation, https://wingedseal.github.io/docs.jmc/")
        print(f"Edit the configuration and run again.")
        system("pause")


if __name__ == '__main__':
    main()
