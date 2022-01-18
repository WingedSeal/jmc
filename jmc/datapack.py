from typing import Dict, List, Set, TYPE_CHECKING
from collections import defaultdict
from pathlib import Path
import regex
import json
import re

from .flow_control.function_ import Function, process_function
from .command import Command
from .config import configs
from .utils import split
from . import Logger


logger = Logger(__name__)


class DataPack:
    from .flow_control.function_ import process_function
    from .flow_control.class_ import process_class
    from .flow_control.if_else import process_if_else
    from .flow_control.for_ import process_for
    from .flow_control.while_ import process_while

    def __init__(self) -> None:
        self.namespace: str = configs['namespace']
        self.description: str = configs['description']
        self.pack_format: int = configs['pack_format']
        self.jmc_path = Path(configs['target'])
        self.datapack_path = Path(configs['output'])

        self.scoreboards: Set[str] = {'__int__', '__variable__'}
        self.ints: Set[int] = set()
        self.functions: Dict[str, Function] = dict()
        self.private_functions: Dict[str,
                                     Dict[str, Function]] = defaultdict(dict)
        self.__private_function_count: Dict[str, int] = defaultdict(int)

    def init(self) -> None:
        logger.info("Reading files")
        with self.jmc_path.open('r') as jmc_file:
            string = jmc_file.read()

        logger.info("Deleting comments")
        string = re.sub(r"# .*|\/\/.*", "", string)

        logger.info("Deleting Newlines")
        string = re.sub(r"\n", " ", string)

        lines = split(string, ';')

        def import_found(match: re.Match):
            path: str = match.groups()[0]
            if not path.endswith(".jmc"):
                path += '.jmc'
            logger.info(f'Import found - {path}')

            with (self.jmc_path.parent/path).open('r') as file:
                content = file.read()

            return content

        for i, line in enumerate(lines):
            if line == '':
                continue
            content, success = regex.subn(
                r"^@import [\'\"](.*?)[\'\"]", import_found, line, count=1)
            if success:
                lines[i] = content

        string = ";".join(lines)

        logger.info("Deleting comments")
        string = re.sub(r"# .*|\/\/.*", "", string)

        logger.info("Replacing Newlines")
        string = re.sub(r"\n", " ", string)

        lines = split(string, ';')

        load_content = ''

        for line in lines:
            line = self.process_class(line)
            line = self.process_function(line)
            load_content += f'{line};'

        commands = self.process_function_content(load_content)
        self.functions[f'__load__'] = Function(commands)

        logger.info(repr(self))

    def process_function_content(self, content: str) -> List[Command]:
        logger.debug(f"Proccessing Function's content\n{content.strip()}")
        lines = split(content, ';')
        commands = []
        for line in lines:
            command = self.process_line(line)
            if line != '':
                commands += command
        return commands

    def process_flow_control(self, line: str):
        logger.debug("Proccessing Flow Controls")
        if line == '':
            return ''
        logger.debug(line)

        line, success = self.process_if_else(line)
        if success:
            return self.process_flow_control(line)

        line, success = self.process_for(line)
        if success:
            return self.process_flow_control(line)

        line, success = self.process_while(line)
        if success:
            return self.process_flow_control(line)

        return line

    def process_line(self, line: str) -> Command:
        logger.debug(f"Proccessing Line\n{line.strip()}")
        commands = []
        line = self.process_flow_control(line)
        lines = split(line, ';')
        for line in lines:
            if line != '':
                commands.append(Command(line, self))

        return commands

    def get_pfc(self, string: str) -> str:
        count = self.__private_function_count[string]
        self.__private_function_count[string] += 1
        return str(count)

    def __repr__(self) -> str:
        functions_string = json.dumps(
            {name: [str(command) for command in func.commands] for name, func in self.functions.items()}, indent=2)

        private_functions_string = json.dumps(
            {key: {name: [str(command) for command in func.commands] for name, func in functions.items()} for key, functions in self.private_functions.items()}, indent=2)

        return f"""DataPack
        Scoreboards - {self.scoreboards}
        Ints - {self.ints}
        Functions\n{functions_string}
        Private Functions{private_functions_string}
        """

    def compile(self) -> None:
        logger.info("Compiling, Exporting to files")
        self.datapack_path.mkdir(exist_ok=True)
        with (self.datapack_path/'pack.mcmeta').open(mode='w+') as file:
            json.dump({
                "pack": {
                      "pack_format": self.pack_format,
                      "description": self.description
                      }
            }, file, indent=2)
        minecraft_function_path = self.datapack_path / \
            'data'/'minecraft'/'tags'/'functions'
        namespace_path = self.datapack_path/'data'/self.namespace
        function_path = namespace_path/'functions'

        minecraft_function_path.mkdir(exist_ok=True, parents=True)
        namespace_path.mkdir(exist_ok=True, parents=True)
        function_path.mkdir(exist_ok=True, parents=True)

        # Handle __load__
        __load__ = "\n".join(
            [f'scoreboard objectives add {obj} dummy' for obj in self.scoreboards] +
            [f'scoreboard players set {integer} __int__ {integer}' for integer in self.ints] +
            [''] +
            [str(command) for command in self.functions["__load__"].commands]
        )
        with (minecraft_function_path/'load.json').open(mode='w+') as file:
            string = file.read()
            if string == "":
                dictionary = {"values": []}
            else:
                dictionary: dict = json.loads(string)
            dictionary["replace"] = False
            dictionary["values"].append(f"{self.namespace}:__load__")
            json.dump(dictionary, file, indent=2)
        with (function_path/'__load__.mcfunction').open(mode='w+') as file:
            file.write(__load__)
        del self.functions["__load__"]

        # Handle __tick__
        if '__tick__' in self.functions:
            with (minecraft_function_path/'tick.json').open(mode='w+') as file:
                string = file.read()
                if string == "":
                    dictionary = {"values": []}
                else:
                    dictionary: dict = json.loads(string)
                dictionary["replace"] = False
                dictionary["values"].append(f"{self.namespace}:__tick__")
                json.dump(dictionary, file, indent=2)

        for name, function in self.functions.items():
            path = function_path/f'{name.replace(".","/").lower()}.mcfunction'
            path.parent.mkdir(exist_ok=True, parents=True)
            with path.open(mode='w+') as file:
                file.write("\n".join([str(command)
                           for command in function.commands]))

        for func_type, functions in self.private_functions.items():
            for func_name, func in functions.items():
                path = function_path / \
                    f'__private__/{func_type}/{func_name.replace(".","/").lower()}.mcfunction'
                path.parent.mkdir(exist_ok=True, parents=True)
                with path.open(mode='w+') as file:
                    file.write("\n".join([str(command)
                                          for command in func.commands]))
