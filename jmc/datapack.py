from collections import defaultdict
from shutil import rmtree
from pathlib import Path
import regex
import json
import re

from .flow_control import Function
from .command import Command
from .config import configs
from .utils import split
from . import Logger


logger = Logger(__name__)


class DataPack:
    from .flow_control import capture_new, capture_function, capture_if_else, capture_class, capture_for, capture_while

    def __init__(self) -> None:
        self.namespace: str = configs['namespace']
        self.description: str = configs['description']
        self.pack_format: int = configs['pack_format']
        self.jmc_path = Path(configs['target'])
        self.datapack_path = Path(configs['output'])

        self.scoreboards: set[str] = {'__int__', '__variable__'}
        self.ints: set[int] = set()
        self.functions: dict[str, Function] = dict()
        self.private_functions: dict[str,dict[str, Function]] = defaultdict(dict) #noqa
        self.__private_function_count: dict[str, int] = defaultdict(int)
        self.news: dict[str, dict[str, dict]] = defaultdict(dict)

    def handle_import_coment(self, string: str) -> str:
        import_success = False

        logger.info("Deleting comments")
        def regex_comment(match: re.Match):
            groups = match.groups()
            if groups[2] is None:
                return match.group(0)
            return ""
        string = regex.sub(r"(\\*[\"'])((?:\\{2})*|(?:.*?[^\\](?:\\{2})*))\1|(# .*|\/\/.*)", regex_comment, string)
        logger.info("Replacing Newlines")
        string = re.sub(r"\n", " ", string)

        logger.info("Replacing imports")
        def regex_import(match: re.Match) -> str:
            groups = match.groups()
            if groups[2] is None:
                return match.group(0)

            nonlocal import_success 
            import_success = True
            path: str = match.groups()[4]
            if not path.endswith(".jmc"):
                path += '.jmc'
            logger.info(f'Import found - {path}')
            with (self.jmc_path.parent/path).open('r') as file:
                content = file.read()
            return content
        
        string = regex.sub(r"(\\*[\"'])((?:\\{2})*|(?:.*?[^\\](?:\\{2})*))\1|(@import ([\'\"])(.*?)\4;)", regex_import, string)

        if import_success:
            string = self.handle_import_coment(string)

        return string


    def init(self) -> None:
        logger.info("Reading files")
        with self.jmc_path.open('r') as jmc_file:
            string = jmc_file.read()

        string = self.handle_import_coment(string)

        lines = split(string, ';')

        load_content = ''

        for line in lines:
            line = self.capture_class(line)
            line = self.capture_new(line)
            line = self.capture_function(line)
            load_content += f'{line};'

        commands = self.process_function_content(load_content)
        self.functions[f'__load__'] = Function(commands)

        logger.info(repr(self))

    def process_function_content(self, content: str) -> list[Command]:
        logger.debug(f"Proccessing Function's content\n{content.strip()}")
        lines = split(content, ';')
        commands = []
        for line in lines:
            command = self.process_line(line)
            if line != '':
                commands += command
        return commands

    def capture_flow_control(self, line: str):
        logger.debug("Proccessing Flow Controls")
        if line == '':
            return ''
        logger.debug(line)

        line, success = self.capture_if_else(line)
        if success:
            return self.capture_flow_control(line)

        line, success = self.capture_for(line)
        if success:
            return self.capture_flow_control(line)

        line, success = self.capture_while(line)
        if success:
            return self.capture_flow_control(line)

        return line

    def process_line(self, line: str) -> Command:
        logger.debug(f"Proccessing Line\n{line.strip()}")
        commands = []
        line = self.capture_flow_control(line)
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

    def clean_up(self) -> None:
        namespace_path = self.datapack_path/'data'/self.namespace
        if namespace_path.exists():
            rmtree(namespace_path.as_posix())

    def compile(self) -> None:
        self.clean_up()
        logger.info("Compiling, Exporting to files")
        self.datapack_path.mkdir(exist_ok=True)
        with (self.datapack_path/'pack.mcmeta').open(mode='w+') as file:
            json.dump({
                "pack": {
                      "pack_format": self.pack_format,
                      "description": self.description
                      }
            }, file, indent=2)
        minecraft_function_path = self.datapack_path/'data'/'minecraft'/'tags'/'functions' # noqa
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

        # Create functions
        for name, function in self.functions.items():
            path = function_path/f'{name}.mcfunction'
            path.parent.mkdir(exist_ok=True, parents=True)
            with path.open(mode='w+') as file:
                file.write("\n".join([str(command)
                           for command in function.commands]))

        # Create private functions
        for func_type, functions in self.private_functions.items():
            for func_name, func in functions.items():
                path = function_path/'__private__'/func_type/f'{func_name}.mcfunction' #noqa
                path.parent.mkdir(exist_ok=True, parents=True)
                with path.open(mode='w+') as file:
                    file.write("\n".join([str(command)
                                          for command in func.commands]))

        # Create news
        for new_type, contents in self.news.items():
            for new_name, content in contents.items():
                path = namespace_path/new_type/f'{new_name}.json'
                path.parent.mkdir(exist_ok=True, parents=True)
                with path.open(mode='w+') as file:
                    json.dump(content, file, indent=2)