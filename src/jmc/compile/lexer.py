from copy import deepcopy
from pathlib import Path
from json import loads, JSONDecodeError, dumps
from typing import TYPE_CHECKING


from .decorator_parse import DECORATORS
from .header import Header
from .exception import JMCDecodeJSONError, JMCFileNotFoundError, JMCSyntaxException, MinecraftSyntaxWarning, relative_file_name
from .tokenizer import Tokenizer, Token, TokenType
from .datapack import DataPack, Function, PreFunction
from .log import Logger
from .utils import convention_jmc_to_mc, deep_merge, is_decorator, search_to_string
from .command import parse_condition
from .lexer_func_content import FuncContent

if TYPE_CHECKING:
    from ..terminal import Configuration

logger = Logger(__name__)


JSON_FILE_TYPES = [
    "advancements",
    "dimension",
    "dimension_type",
    "loot_tables",
    "predicates",
    "recipes",
    "item_modifiers",
    "structures",
    "worldgen/biome",
    "worldgen/configured_carver",
    "worldgen/configured_feature",
    "worldgen/configured_surface_builder",
    "worldgen/density_function",
    "worldgen/flat_level_generator_preset",
    "worldgen/noise",
    "worldgen/noise_settings",
    "worldgen/placed_feature",
    "worldgen/processor_list",
    "worldgen/structure",
    "worldgen/structure_set",
    "worldgen/template_pool",
    "worldgen/world_preset",
    "trim_material",
    "trim_pattern",
    "chat_type",
    "damage_type"
]
"""List of all possible vanilla json file types"""

JMC_JSON_FILE_TYPES = {
    "advancement": "advancements",
    "loot_table": "loot_tables",
    "structure": "structures",
    "recipe": "recipes",
}
"""Dictionary of JMC's custom file type that'll be automatically converted to vanilla ones"""


class Lexer:
    """
    Lexical Analyizer

    :param config: JMC configuration
    """
    __slots__ = (
        "if_else_box",
        "load_tokenizer",
        "do_while_box",
        "imports",
        "config",
        "datapack")

    if_else_box: list[tuple[Token | None, Token | list[Token]]]
    """List of tuple of condition(Token) and code block(paren_curly Token) in if-else chain"""
    load_tokenizer: Tokenizer
    """Tokenizer for load function"""
    do_while_box: Token | None
    """paren_curly token for code block of `do` in `do while`"""
    imports: set[Path]
    """Set of path that's already imported"""
    config: "Configuration"
    """JMC configuration"""
    datapack: DataPack
    """Datapack object"""

    def __init__(self, config: "Configuration",
                 _test_file: str | None = None) -> None:
        logger.debug("Initializing Lexer")
        self.do_while_box = None
        self.imports = set()
        self.if_else_box = []
        self.config = config
        self.datapack = DataPack(
            config.namespace, int(
                config.pack_format), self)
        self.datapack.functions[self.datapack.load_name] = Function()
        self.parse_file(Path(self.config.target), _test_file, is_load=True)

        logger.debug("Load Function")

    def __update_load(self, file_path_str: str, raw_str: str):
        if file_path_str == self.load_tokenizer.file_path:
            return
        self.load_tokenizer.file_path = file_path_str
        self.load_tokenizer.raw_string = raw_str
        self.load_tokenizer.file_string = raw_str

    def parse_current_load(self):
        """Parse current load function that's in self.datapack.load_function and clear it"""
        if self.datapack.load_function:
            self.datapack.functions[self.datapack.load_name].extend(
                self.parse_load_func_content(programs=self.datapack.load_function))
            self.datapack.load_function = []

    def parse_file(self, file_path: Path, _test_file: str | None = None,
                   is_load=False) -> None:
        """
        Parse JMC file

        :param file_path: Path to file to parse
        :param is_load: Whether the file is for load function, defaults to False
        :raises JMCFileNotFoundError: Can't find the JMC file
        :raises JMCSyntaxException: Nothing after `@import`
        :raises JMCSyntaxException: A token after `@import` is not a string
        :raises JMCSyntaxException: Unexpected argument token in `@import`
        :raises JMCSyntaxException: Path in `@import` is invalid
        :raises JMCSyntaxException: _description_
        """
        if file_path in self.datapack._imported:
            return
        self.datapack._imported.add(file_path)
        logger.info(f"Parsing file: {file_path}")
        file_path_str = file_path.resolve().as_posix()
        if _test_file is None:
            try:
                with file_path.open("r", encoding="utf-8") as file:
                    raw_string = file.read()
            except FileNotFoundError as error:
                raise JMCFileNotFoundError(
                    f"JMC file not found: {file_path.resolve().as_posix()}") from error
        else:
            raw_string = _test_file
        tokenizer = Tokenizer(raw_string, file_path_str)
        if is_load:
            self.load_tokenizer = deepcopy(tokenizer)

        self.__update_load(file_path_str, raw_string)

        for command in tokenizer.programs:
            if command[0].string == "function" and not self._is_vanilla_func(
                    command):
                self.parse_current_load()
                self.parse_func(tokenizer, command, file_path_str)
            elif is_decorator(command[0].string):
                self.parse_current_load()
                self.parse_decorated_function(
                    tokenizer, command, file_path_str)
            elif command[0].string == "new":
                self.parse_current_load()
                self.parse_new(tokenizer, command)
            elif command[0].string == "class":
                self.parse_current_load()
                self.parse_class(tokenizer, command, file_path_str)
            elif command[0].string == "import":
                self.parse_current_load()
                if len(command) < 2:
                    raise JMCSyntaxException(
                        "Expected string after '@import'", command[0], tokenizer, col_length=True)
                if command[1].token_type != TokenType.STRING:
                    raise JMCSyntaxException(
                        "Expected string after '@import'", command[1], tokenizer)
                if len(command) > 2:
                    raise JMCSyntaxException(
                        "Unexpected token", command[1], tokenizer, display_col_length=False)
                if command[1].string.endswith(
                        "/*") or command[1].string.endswith("\\*"):
                    try:
                        folder = Path(command[1].string[:-2])
                    except Exception as error:
                        raise JMCSyntaxException(
                            f"Unexpected invalid path ({command[1].string})", command[1], tokenizer) from error
                    if not folder.is_dir():
                        raise JMCFileNotFoundError(
                            f"Directory(folder) not found: {folder.resolve().as_posix()}")

                    new_paths = folder.glob("**/*.jmc")
                    for new_path in new_paths:
                        self.parse_file(file_path=new_path.resolve())
                        self.__update_load(file_path_str, raw_string)
                    continue
                try:
                    new_path = Path(
                        (file_path.parent / command[1].string).resolve()
                    )
                    if new_path.suffix != ".jmc":
                        new_path = Path(
                            (file_path.parent /
                             (command[1].string + ".jmc")).resolve()
                        )
                except Exception as error:
                    raise JMCSyntaxException(
                        f"Unexpected invalid path ({command[1].string})", command[1], tokenizer) from error
                self.parse_file(file_path=new_path)
                self.__update_load(file_path_str, raw_string)
            else:
                self.datapack.load_function.append(command)

        self.parse_current_load()

    def parse_decorated_function(self, tokenizer: Tokenizer,
                                 command: list[Token], file_path_str: str, prefix: str = ''):
        decorator_name = command[0].string[1:]
        if decorator_name not in DECORATORS:
            raise JMCSyntaxException(
                f"Unrecognized decorator '{decorator_name}'",
                command[0],
                tokenizer,
                suggestion="Did you mean to write 'import' instead?" if decorator_name == "import" else None)
        jmc_decorator = DECORATORS[decorator_name]
        if len(command) < 5:
            raise JMCSyntaxException(
                "Function decorator expected '@decorator_name function name() {}' or '@decorator_name() function name() {}'",
                command[0],
                tokenizer)
        if command[1].token_type == TokenType.PAREN_ROUND:
            function_commands = command[2:]
            args = command[1]
        else:
            function_commands = command[1:]
            args = None
        pre_function = self.parse_func_tokens(
            tokenizer,
            function_commands,
            file_path_str,
            prefix,
            is_save_to_datapack=jmc_decorator.is_save_to_datapack)
        func_object = None
        if jmc_decorator.is_save_to_datapack:
            func_object = pre_function.parse()
            self.datapack.functions[pre_function.func_path] = func_object
        jmc_decorator(
            tokenizer,
            command,
            self.datapack,
            prefix,
            args).modify(
            pre_function, func_object)

    def parse_func_tokens(self, tokenizer: Tokenizer,
                          command: list[Token], file_path_str: str, prefix: str = '', is_save_to_datapack: bool = True) -> PreFunction:
        """
        Parse a function definition in form of list of token

        :param tokenizer: Tokenizer
        :param command: List of token inside a function definition
        :param file_path_str: File path to current JMC function as string
        :param prefix: Prefix of function(for Class feature), defaults to ''
        :param is_save_to_datapack: Whether to save the result function into the datapack, defaults to True
        :return: func_content, file_path_str, line, col, file_string, func_path
        :raises JMCSyntaxException: Function name isn't keyword token
        :raises JMCSyntaxException: Function name is not followed by paren_round token
        :raises JMCSyntaxException: paren_round token isn't followed by paren_curly token
        :raises JMCSyntaxException: Start function name with JMC's PRIVATE_NAME
        :raises JMCSyntaxException: Duplicate function declaration
        :raises JMCSyntaxException: Define load function
        :raises JMCSyntaxException: Define private function
        """
        logger.debug(f"Parsing function, prefix = {prefix!r}")
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected keyword(function's name)", command[0], tokenizer, display_col_length=True, col_length=True)
        if command[1].token_type != TokenType.KEYWORD:
            raise JMCSyntaxException(
                "Expected keyword(function's name)", command[1], tokenizer)
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected round bracket, `()`", command[1], tokenizer, display_col_length=True, col_length=True)
        if is_save_to_datapack and command[2].string != "()":
            raise JMCSyntaxException(
                "Expected empty round bracket, `()`", command[2], tokenizer)
        if len(command) < 4:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, display_col_length=True, col_length=True)
        if command[3].token_type != TokenType.PAREN_CURLY:
            raise JMCSyntaxException(
                "Expected {", command[3], tokenizer, display_col_length=False)
        if len(command) > 4:
            raise JMCSyntaxException(
                "Unexpected token", command[4], tokenizer)

        func_path = prefix + \
            convention_jmc_to_mc(command[1], tokenizer, prefix="")
        if func_path.startswith(DataPack.private_name + "/"):
            raise JMCSyntaxException(
                f"Function({func_path}) may override private function of JMC", command[1], tokenizer, suggestion=f"Please avoid starting function's path with {DataPack.private_name}")
        logger.debug(f"Function: {func_path}")
        func_content = command[3].string[1:-1]
        if func_path == self.datapack.load_name:
            raise JMCSyntaxException(
                "Load function is defined", command[1], tokenizer)
        if func_path in self.datapack.functions:
            old_function_token, old_function_tokenizer = self.datapack.defined_file_pos[
                func_path]
            raise JMCSyntaxException(
                f"Duplicate function declaration({func_path})", command[1], tokenizer,
                suggestion=f"This function was already defined at line {old_function_token.line} col {old_function_token.col} in {relative_file_name(old_function_tokenizer.file_path, old_function_token.line, old_function_token.col)}")
        if func_path == self.datapack.private_name:
            raise JMCSyntaxException(
                "Private function is defined", command[1], tokenizer, display_col_length=False)
        self.datapack.defined_file_pos[func_path] = (command[1], tokenizer)
        return PreFunction(func_content, file_path_str,
                           command[3].line, command[3].col, tokenizer.file_string, func_path, command[1], command[2], self, tokenizer, prefix)

    def parse_func(self, tokenizer: Tokenizer,
                   command: list[Token], file_path_str: str, prefix: str = '', is_save_to_datapack: bool = True) -> tuple[Function, str]:
        """
        Parse a function definition in form of list of token

        :param tokenizer: Tokenizer
        :param command: List of token inside a function definition
        :param file_path_str: File path to current JMC function as string
        :param prefix: Prefix of function(for Class feature), defaults to ''
        :param is_save_to_datapack: Whether to save the result function into the datapack, defaults to True
        :return: A tuple of Function and its path string
        :raises JMCSyntaxException: Function name isn't keyword token
        :raises JMCSyntaxException: Function name is not followed by paren_round token
        :raises JMCSyntaxException: paren_round token isn't followed by paren_curly token
        :raises JMCSyntaxException: Start function name with JMC's PRIVATE_NAME
        :raises JMCSyntaxException: Duplicate function declaration
        :raises JMCSyntaxException: Define load function
        :raises JMCSyntaxException: Define private function
        """
        pre_function = self.parse_func_tokens(
            tokenizer, command, file_path_str, prefix, is_save_to_datapack)
        return_value = pre_function.parse()
        if is_save_to_datapack:
            self.datapack.functions[pre_function.func_path] = return_value
        return return_value, pre_function.func_path

    def _is_vanilla_func(self, command: list[Token]) -> bool:
        """
        Whether command is in vanilla function syntax
        """
        if len(command) == 2 and command[1].token_type == TokenType.STRING:
            return True
        if not (
            len(command) >= 4 and
            command[1].token_type == TokenType.KEYWORD and
            command[2].token_type == TokenType.OPERATOR and
            command[2].string == ":" and
            command[3].token_type == TokenType.KEYWORD
        ):
            return False
        if len(command) > 4:
            command = command.copy()
            # Clear paths
            for index, token in enumerate(command[4::2]):
                if token.string == "/" and len(command) > index + 1:
                    del command[index]
                    del command[index + 1]

        if len(command) == 4:
            return True
        if len(
                command) == 5 and command[4].token_type == TokenType.PAREN_CURLY:
            return True
        if (
            len(command) >= 5 and
            command[4].string == "with"
        ):
            return True
        return False

    def parse_new(self, tokenizer: Tokenizer,
                  command: list[Token], prefix: str = ''):
        """
        Parse a new json definition in form of list of token

        :param tokenizer: Tokenizer
        :param command: List of token inside a new json definition
        # :param file_path_str: File path to current JMC function as string
        :param prefix: Prefix of json(for Class feature), defaults to ''
        :raises JMCSyntaxException: JSON file's type is not given
        :raises JMCSyntaxException: JSON file's type is not a keyword token
        :raises JMCSyntaxException: JSON file's type is not followed by JSON file's path
        :raises JMCSyntaxException: JSON file's path is not a paren_round token
        :raises JMCSyntaxException: JSON file's path is not followed by paren_round token
        :raises JMCSyntaxException: paren_round token is not followed by anything
        :raises JMCSyntaxException: paren_round token is not followed by paren_curly token
        :raises MinecraftSyntaxWarning: JSON file's type isn't in JSON_FILE_TYPES
        :raises MinecraftSyntaxWarning: Uppercase letter found in JSON file's path
        :raises JMCSyntaxException: Start JSON file's name with JMC's PRIVATE_NAME
        :raises JMCSyntaxException: Duplicate new json declaration
        :raises JMCDecodeJSONError: Invalid JSON
        """
        logger.debug(f"Parsing 'new' keyword, prefix = {prefix!r}")
        has_extends_arg = False
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected keyword(JSON file's type)", command[0], tokenizer, col_length=True)
        if command[1].token_type != TokenType.KEYWORD:
            raise JMCSyntaxException(
                "Expected keyword(JSON file's type)", command[1], tokenizer)
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected round bracket(JSON file's path)", command[1], tokenizer, col_length=True)
        if command[2].string == "()":
            raise JMCSyntaxException(
                "Expected JSON file's path in the bracket", command[2], tokenizer)
        if command[2].token_type != TokenType.PAREN_ROUND:
            raise JMCSyntaxException(
                "Expected (", command[1], tokenizer)
        if len(command) < 4:
            raise JMCSyntaxException(
                "Expected { or [", command[2], tokenizer, col_length=True)
        if command[3].string == "extends":
            if command[4].token_type != TokenType.PAREN_ROUND:
                raise JMCSyntaxException(
                    "Expected (", command[3], tokenizer)
            has_extends_arg = True
        elif command[3].token_type not in {
                TokenType.PAREN_CURLY, TokenType.PAREN_SQUARE}:
            raise JMCSyntaxException(
                "Expected { or [", command[3], tokenizer)

        json_type = convention_jmc_to_mc(
            command[1], tokenizer, is_make_lower=False, prefix="")

        if json_type not in JSON_FILE_TYPES and not json_type.startswith(
                "tags/"):
            if json_type in JMC_JSON_FILE_TYPES:
                json_type = JMC_JSON_FILE_TYPES[json_type]
            elif json_type.startswith("tag/"):
                json_type = json_type.replace("tag/", "tags/")
            else:
                raise MinecraftSyntaxWarning(
                    f"Unrecognized JSON file's type({json_type})", command[1], tokenizer, suggestion="The 'minecraft.' prefix is supposed to go *inside* the parentheses." if json_type.startswith("minecraft") else None
                )

        json_name = prefix + convention_jmc_to_mc(
            command[2], tokenizer, is_make_lower=False, substr=(1, -1), prefix="")

        namespace = json_name.split("/")[0]
        if namespace in Header().namespace_overrides:
            json_path = namespace + "/" + json_type + \
                "/" + json_name[len(namespace) + 1:]
        else:
            json_path = json_type + "/" + json_name

        if not json_path.islower():
            raise MinecraftSyntaxWarning(
                f"Uppercase letter found in JSON file's path({json_path})", command[
                    2], tokenizer
            )
        if json_path.startswith(DataPack.private_name + "/"):
            raise JMCSyntaxException(
                f"JSON({json_path}) may override private function of JMC", command[2], tokenizer, suggestion=f"Please avoid starting JSON's path with {DataPack.private_name}")

        logger.debug(f"JSON: {json_type}({json_path})")
        json_content = command[-1].string
        if json_path in self.datapack.jsons:
            old_json_token, old_json_tokenizer = self.datapack.defined_file_pos[
                json_path]
            raise JMCSyntaxException(
                f"Duplicate JSON({json_path})", command[2], tokenizer,
                suggestion=f"This json was already defined at line {old_json_token.line} col {old_json_token.col} in {old_json_tokenizer.file_path}")

        try:
            json: dict[str, str] = loads(json_content, strict=False)
        except JSONDecodeError as error:
            raise JMCDecodeJSONError(error, command[-1], tokenizer) from error
        if not json:
            raise JMCSyntaxException(
                "JSON content cannot be empty", command[-1], tokenizer)

        if has_extends_arg:
            super_name = convention_jmc_to_mc(
                command[4], tokenizer, prefix="", is_make_lower=False, substr=(1, -1))
            if namespace in Header().namespace_overrides:
                super_path = namespace + "/" + json_type + \
                    "/" + super_name[len(namespace) + 1:]
            else:
                super_path = json_type + "/" + super_name

            try:
                super_json = self.datapack.jsons[super_path]
            except KeyError:
                raise JMCSyntaxException(
                    f"Invalid JSON({super_path})", command[2], tokenizer,
                    suggestion=f"Make sure you have created a previous JSON file at that path and you are spelling its name correctly")

            assert isinstance(super_json, dict)
            json = deep_merge(super_json, json)

        self.datapack.defined_file_pos[json_path] = (command[1], tokenizer)
        self.datapack.jsons[json_path] = json

    def parse_class(self, tokenizer: Tokenizer,
                    command: list[Token], file_path_str: str, prefix: str = ''):
        """
        _summary_

        :param tokenizer: Tokenizer
        :param command: List of token inside a class definition
        :param file_path_str: File path to current JMC function as string
        :param prefix: Prefix of class(for Class feature), defaults to '', defaults to ''
        :raises JMCSyntaxException: Class's name is not given
        :raises JMCSyntaxException: Class's name is not a keyword token
        :raises JMCSyntaxException: Class's name is not followed by anything
        :raises JMCSyntaxException: Class's name is not followed by paren_round token
        """
        logger.debug(f"Parsing Class, prefix = {prefix!r}")
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected keyword(class's name)", command[0], tokenizer)
        if command[1].token_type != TokenType.KEYWORD:
            raise JMCSyntaxException(
                "Expected keyword(class's name)", command[1], tokenizer)
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected {", command[1], tokenizer, col_length=True)
        if command[2].token_type != TokenType.PAREN_CURLY:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer)

        class_path = prefix + \
            convention_jmc_to_mc(command[1], tokenizer, prefix="")
        class_content = command[2].string[1:-1]
        self.parse_class_content(class_path + "/",
                                 class_content, file_path_str, line=command[2].line, col=command[2].col, file_string=tokenizer.file_string)

    def parse_load_func_content(
            self, programs: list[list[Token]]) -> list[str]:
        """
        Parse content inside load function

        :param programs: List of commands(List of arguments(Token))
        :return: List of commands(string)
        """
        tokenizer = self.load_tokenizer
        return self._parse_func_content(
            tokenizer, programs, prefix="", is_load=True)

    def parse_line(self, tokens: list[Token],
                   tokenizer: Tokenizer, prefix: str) -> list[str]:
        """
        Parse just a line of command(List of arguments(Token))

        :param tokens: A minecraft command(List of arguments(Token))
        :param tokenizer: Tokenizer
        :return: List of minecraft commands
        """
        return self._parse_func_content(
            tokenizer, [tokens], prefix, is_load=False)

    def parse_func_content(self,
                           func_content: str, file_path_str: str,
                           line: int, col: int, file_string: str, prefix: str) -> list[str]:
        """
        Parse function's content

        :param func_content: String containing function's content
        :param file_path_str: File path to current JMC function as string
        :param line: Current line in current JMC function
        :param col: Current column in current JMC function
        :param file_string: Content of current JMC function
        :return: List of commands(string)
        """
        tokenizer = Tokenizer(func_content, file_path_str,
                              line=line, col=col, file_string=file_string)
        programs = tokenizer.programs
        return self._parse_func_content(
            tokenizer, programs, prefix, is_load=False)

    def _parse_func_content(self, tokenizer: Tokenizer,
                            programs: list[list[Token]], prefix: str, is_load: bool) -> list[str]:
        """
        Parse a content inside function
        :param tokenizer: Tokenizer
        :param programs: List of commands(List of arguments(Token))
        :param is_load: Whether the function is a load function

        :return: List of commands(String)
        """

        return FuncContent(tokenizer, programs, is_load, self, prefix).parse()

    def parse_class_content(self, prefix: str, class_content: str,
                            file_path_str: str, line: int, col: int, file_string: str) -> None:
        """
        Parse content of a class

        :param prefix: Prefix of class(for Class feature)
        :param class_content: Content inside class as string
        :param file_path_str: File path to current JMC function as string
        :param line: Current line in current JMC function
        :param col: Current column in current JMC function
        :param file_string: Content of current JMC function
        :raises JMCSyntaxException: Importing in class
        :raises JMCSyntaxException: Got something else beside 'function' or 'new' or 'class'
        """
        tokenizer = Tokenizer(class_content, file_path_str,
                              line=line, col=col, file_string=file_string)
        for command in tokenizer.programs:
            if command[0].string == "function" and len(command) == 4:
                self.parse_func(tokenizer, command, file_path_str, prefix)
            elif is_decorator(command[0].string):
                self.parse_decorated_function(
                    tokenizer, command, file_path_str, prefix)
            elif command[0].string == "new":
                self.parse_new(tokenizer, command, prefix)
            elif command[0].string == "class":
                self.parse_class(tokenizer, command, file_path_str, prefix)
            elif command[0].string == "import":
                raise JMCSyntaxException(
                    "Importing is not supported in class", command[0], tokenizer)
            else:
                raise JMCSyntaxException(
                    f"Expected 'function' or 'new' or 'class' (got {command[0].string})", command[0], tokenizer)

    def parse_if_else(self, tokenizer: Tokenizer, prefix: str,
                      name: str = "if_else", is_expand: bool = False, is_macro: bool = False) -> str:
        """
        Parse if-else chain using if_else_box attribute

        :param tokenizer: Tokenizer
        :param name: Private function's group name, defaults to 'if_else'
        :return: A minecraft command to initiate the if-else chain
        """
        VAR = "__if_else__"

        logger.debug(f"Handling if-else (name={name}, is_expand={is_expand})")
        if_else_box = self.if_else_box
        self.if_else_box = []
        if if_else_box[0][0] is None:
            raise ValueError("if_else_box[0][0] is None")
        condition, precommand = parse_condition(
            if_else_box[0][0], tokenizer, self.datapack)

        if is_expand:
            expanded_commands = self.datapack.parse_function_token(
                if_else_box[0][1], tokenizer, prefix)
            output = []
            for expanded_command in expanded_commands:
                if "\n" in expanded_command:
                    output.append(
                        f"{precommand}execute {condition} run {self.datapack.add_private_function('expand', expanded_command)}")
                elif expanded_command.startswith("execute "):
                    output.append(
                        f"{precommand}execute {condition} {expanded_command[8:]}")
                else:
                    output.append(
                        f"{precommand}execute {condition} run {expanded_command}")
            return "\n".join(output)

        # Case 1: `if` only
        if len(if_else_box) == 1:
            arrow_func = self.datapack.add_arrow_function(
                name, if_else_box[0][1], tokenizer, prefix)
            if is_macro:
                precommand = f"${precommand}"
            if arrow_func.startswith("execute "):
                # len('execute ') = 8
                return f"{precommand}execute {condition} {arrow_func[8:]}"
            return f"{precommand}execute {condition} run {arrow_func}"

        # Case 2: Has `else` or `else if`
        conditions = [f"{precommand}execute {condition} run"]
        command_tokens = [if_else_box[0][1]]
        del if_else_box[0]

        if if_else_box[-1][0] is None:
            else_ = if_else_box[-1][1]
            del if_else_box[-1]
        else:
            else_ = None

        count_tmp = ""
        # `else if`
        if if_else_box:
            for else_if in if_else_box:
                if else_if[0] is None:
                    raise ValueError("else_if[0] is None")
                condition, precommand = parse_condition(
                    else_if[0], tokenizer, self.datapack)
                conditions.append(f"{precommand}execute {condition} run")
                command_tokens.append(else_if[1])

        # `else`
        outputs = [[f"scoreboard players set {VAR} {DataPack.var_name} 0"]]
        if else_ is None:  # no 'else'
            for condition, command_token in list(
                    zip(conditions, command_tokens))[:-1]:
                outputs[-1].extend([
                    f"""{condition} {self.datapack.add_custom_private_function(name, command_token, tokenizer, prefix=prefix,postcommands=[
                        f'scoreboard players set {VAR} {DataPack.var_name} 1'])}""",
                    f"execute if score {VAR} {DataPack.var_name} matches 0 run "
                ])
                outputs.append([])
            del outputs[-1]
            last_output = f"{conditions[-1]} {self.datapack.add_arrow_function(name, command_tokens[-1], tokenizer, prefix=prefix)}"
        else:  # 'else'
            for condition, command_token in zip(conditions, command_tokens):
                outputs[-1].extend([
                    f"""{condition} {self.datapack.add_custom_private_function(name, command_token, tokenizer, prefix=prefix,postcommands=[
                        f'scoreboard players set {VAR} {DataPack.var_name} 1'])}""",
                    f"execute if score {VAR} {DataPack.var_name} matches 0 run "
                ])
                outputs.append([])
            del outputs[-1]
            last_output = self.datapack.add_arrow_function(
                name, else_, tokenizer, prefix=prefix)

        outputs[-1][-1] = (outputs[-1][-1] +
                           last_output).replace("run execute ", "")
        if len(outputs) > 1:
            count = self.datapack.get_count(name)
            self.datapack.add_private_function(
                name, "\n".join(outputs[-1]), count)
            for output in reversed(outputs[1:-1]):
                output[-1] += self.datapack.call_func(name, count)
                count = self.datapack.get_count(name)
                self.datapack.add_private_function(
                    name, "\n".join(output), count)
            outputs[0][-1] += self.datapack.call_func(name, count)
        return "\n".join(outputs[0])

    def clean_up_paren_token(self, token: Token, tokenizer: Tokenizer,
                             is_nbt: bool = True) -> str:
        """
        Turn a paren token into a clean string

        :param token: paren token
        :param tokenizer: token's Tokenizer
        :param is_nbt: Whether the token is in form of minecraft nbt, defaults to True
        :return: Clean string representing paren token for output
        """
        if len(token.string) == 2:
            return token.string
        open_ = token.string[0]
        close = token.string[-1]
        tokenizer = Tokenizer(token.string[1:-1], tokenizer.file_path, token.line,
                              token.col + 1, tokenizer.file_string, expect_semicolon=False, allow_semicolon=token.token_type == TokenType.PAREN_SQUARE)
        string = ""
        if open_ == "{" and tokenizer.programs[0][0].token_type == TokenType.STRING:
            is_nbt = False
        for token_ in tokenizer.programs[0]:
            if token_.token_type == TokenType.PAREN_ROUND:
                string, success = search_to_string(
                    string, token_, DataPack.var_name, tokenizer)
                if success:
                    _string = ""
                else:
                    _string = self.clean_up_paren_token(
                        token_, tokenizer, is_nbt)
            elif token_.token_type in {TokenType.PAREN_CURLY, TokenType.PAREN_SQUARE}:
                _string = self.clean_up_paren_token(token_, tokenizer, is_nbt)
            elif token_.token_type == TokenType.STRING:
                if is_nbt:
                    _string = repr(token_.string)
                    if '"' not in _string:
                        _string = f'"{_string[1:-1]}"'
                else:
                    _string = dumps(token_.string)
            else:
                _string = token_.string
            string += _string

        return open_ + string + close
