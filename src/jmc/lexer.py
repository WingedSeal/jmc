from pathlib import Path
from json import loads, JSONDecodeError, dumps
from typing import Optional


from .exception import JMCDecodeJSONError, JMCFileNotFoundError, JMCSyntaxException, JMCSyntaxWarning, MinecraftSyntaxWarning
from .vanilla_command import COMMANDS as VANILLA_COMMANDS
from .tokenizer import Tokenizer, Token, TokenType
from .datapack import DataPack, Function
from .log import Logger
from .utils import is_number, is_connected
from .command import (LOAD_ONLY_COMMANDS,
                      EXECUTE_EXCLUDED_COMMANDS,
                      FLOW_CONTROL_COMMANDS,
                      variable_operation,
                      parse_condition,
                      FuncType,
                      JMCFunction,
                      BOOL_FUNCTIONS
                      )
logger = Logger(__name__)

LOAD_ONCE_COMMANDS = JMCFunction._get(FuncType.load_once)
JMC_COMMANDS = JMCFunction._get(FuncType.jmc_command)

JSON_FILE_TYPES = [
    "advancements",
    "dimension",
    "dimension_type",
    "functions",
    "loot_tables",
    "predicates",
    "recipes",
    "structures",
    "tags",
    "worldgen/biome",
    "worldgen/configured_carver",
    "worldgen/configured_feature",
    "worldgen/configured_structure_feature",
    "worldgen/configured_surface_builder",
    "worldgen/noise_settings",
    "worldgen/processor_list",
    "worldgen/template_pool",
]

FIRST_ARGUMENTS = {
    *FLOW_CONTROL_COMMANDS,
    *LOAD_ONCE_COMMANDS,
    *LOAD_ONLY_COMMANDS,
    *JMC_COMMANDS,
    *FLOW_CONTROL_COMMANDS,
    *EXECUTE_EXCLUDED_COMMANDS
} - {'give', 'if'}
"""All vanilla commands and JMC custom syntax 

`if` is excluded from the list since it can be used in execute"""
NEW_LINE = '\n'

ALLOW_NUMBER_AFTER = [
    'give',
    'clear'
]


def append_commands(commands: list[str], string: str) -> None:
    if string.startswith('execute') and commands and commands[-1] == 'run':
        if string == 'execute':
            del commands[-1]
            return
        else:
            del commands[-1]
            commands.append(string[8:])  # len("execute ") = 8
            return
    commands.append(string)
    return


class Lexer:
    load_tokenizer: Tokenizer
    "List of condition string and token"
    do_while_box: Optional[Token] = None

    def __init__(self, config: dict[str, str]) -> None:
        logger.debug("Initializing Lexer")
        self.if_else_box: list[tuple[Optional[Token], Token]] = []
        self.config = config
        self.datapack = DataPack(config["namespace"], self)
        self.parse_file(Path(self.config["target"]), is_load=True)

        logger.debug(f"Load Function")
        self.datapack.functions[self.datapack.LOAD_NAME] = Function(
            self.parse_load_func_content(programs=self.datapack.load_function))

    def parse_file(self, file_path: Path, is_load=False) -> None:
        logger.info(f"Parsing file: {file_path}")
        file_path_str = file_path.resolve().as_posix()
        try:
            with file_path.open('r') as file:
                raw_string = file.read()
        except FileNotFoundError:
            raise JMCFileNotFoundError(
                f"JMC file not found: {file_path.resolve().as_posix()}")
        tokenizer = Tokenizer(raw_string, file_path_str)
        if is_load:
            self.load_tokenizer = tokenizer

        for command in tokenizer.programs:
            if command[0].string == 'function' and len(command) == 4:
                self.parse_func(tokenizer, command, file_path_str)
            elif command[0].string == 'new':
                self.parse_new(tokenizer, command, file_path_str)
            elif command[0].string == 'class':
                self.parse_class(tokenizer, command, file_path_str)
            elif command[0].string == '@import':
                if len(command) < 2:
                    raise JMCSyntaxException(
                        "Expected string after '@import'", command[0], tokenizer, col_length=True)
                if command[1].token_type != TokenType.string:
                    raise JMCSyntaxException(
                        "Expected string after '@import'", command[1], tokenizer)
                if len(command) > 2:
                    raise JMCSyntaxException(
                        "Unexpected token", command[1], tokenizer, display_col_length=False)
                try:
                    new_path = Path(
                        (file_path.parent/command[1].string).resolve()
                    )
                    if new_path.suffix != '.jmc':
                        new_path = Path(
                            (file_path.parent /
                             (command[1].string+'.jmc')).resolve()
                        )
                except Exception:
                    raise JMCSyntaxException(
                        f"Expected invalid path ({command[1].string})", command[1], tokenizer)
                self.parse_file(file_path=new_path)
            else:
                if not is_load:
                    raise JMCSyntaxException(
                        f"Command({command[1].string}) found inside non-load file", command[1], tokenizer)

                self.datapack.load_function.append(command)

    def parse_func(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = '') -> None:
        logger.debug(f"Parsing function, prefix = {prefix!r}")
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                "Expected keyword(function's name)", command[1], tokenizer)
        elif command[2].string != '()':
            raise JMCSyntaxException(
                f"Expected (", command[2], tokenizer, display_col_length=False)
        elif command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                "Expected {", command[3], tokenizer, display_col_length=False)

        func_path = prefix + command[1].string.lower().replace('.', '/')
        if func_path.startswith(DataPack.PRIVATE_NAME+'/'):
            raise JMCSyntaxException(
                f"Function({func_path}) may override private function of JMC", command[1], tokenizer, suggestion=f"Please avoid starting function's path with {DataPack.PRIVATE_NAME}")
        logger.debug(f"Function: {func_path}")
        func_content = command[3].string[1:-1]
        if func_path in self.datapack.functions:
            raise JMCSyntaxException(
                f"Duplicate function declaration({func_path})", command[1], tokenizer, display_col_length=False)
        elif func_path == self.datapack.LOAD_NAME:
            raise JMCSyntaxException(
                "Load function is defined", command[1], tokenizer, display_col_length=False)
        elif func_path == self.datapack.PRIVATE_NAME:
            raise JMCSyntaxException(
                "Private function is defined", command[1], tokenizer, display_col_length=False)
        self.datapack.functions[func_path] = Function(self.parse_func_content(
            func_content, file_path_str, line=command[3].line, col=command[3].col, file_string=tokenizer.file_string))

    def parse_new(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = ''):
        logger.debug(f"Parsing 'new' keyword, prefix = {prefix!r}")
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected keyword(JSON file's type)", command[0], tokenizer, col_length=True)
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                "Expected keyword(JSON file's type)", command[1], tokenizer)
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected JSON file's path in bracket", command[1], tokenizer, col_length=True)
        if command[2].string == '()':
            raise JMCSyntaxException(
                "Expected JSON file's path in bracket", command[2], tokenizer)
        if command[2].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                "Expected (", command[2], tokenizer)
        if len(command) < 4:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, col_length=True)
        if command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                "Expected {", command[3], tokenizer)

        json_type = command[1].string.replace('.', '/')
        if json_type not in JSON_FILE_TYPES:
            raise MinecraftSyntaxWarning(
                f"Unrecognized JSON file's type({json_type})", command[2], tokenizer
            )

        json_path = json_type + '/' + prefix + \
            command[2].string[1:-1].replace('.', '/')
        if not json_path.islower():
            raise MinecraftSyntaxWarning(
                f"Uppercase letter found in JSON file's path({json_path})", command[
                    2], tokenizer
            )
        if json_path.startswith(DataPack.PRIVATE_NAME+'/'):
            raise JMCSyntaxException(
                f"JSON({json_path}) may override private function of JMC", command[2], tokenizer, suggestion=f"Please avoid starting JSON's path with {DataPack.PRIVATE_NAME}")

        logger.debug(f"JSON: {json_type}({json_path})")
        json_content = command[3].string
        if json_path in self.datapack.jsons:
            raise JMCSyntaxException(
                f"Duplicate JSON({json_path})", command[2], tokenizer)

        try:
            json: dict[str, str] = loads(json_content)
        except JSONDecodeError as error:
            raise JMCDecodeJSONError(error, command[3], tokenizer)
        self.datapack.jsons[json_path] = json

    def parse_class(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = ''):
        logger.debug(f"Parsing Class, prefix = {prefix!r}")
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected keyword(class's name)", command[0], tokenizer)
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                "Expected keyword(class's name)", command[1], tokenizer)
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected {", command[1], tokenizer, col_length=True)
        if command[2].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer)

        class_path = prefix + command[1].string.lower().replace('.', '/')
        class_content = command[2].string[1:-1]
        self.parse_class_content(class_path+'/',
                                 class_content, file_path_str, line=command[2].line, col=command[2].col, file_string=tokenizer.file_string)

    def parse_load_func_content(self, programs: list[list[Token]]):
        tokenizer = self.load_tokenizer
        return self._parse_func_content(tokenizer, programs, is_load=True)

    def parse_line(self, tokens: list[Token], tokenizer: Tokenizer) -> list[str]:
        return self._parse_func_content(tokenizer, [tokens], is_load=False)

    def parse_func_content(self,
                           func_content: str, file_path_str: str,
                           line: int, col: int, file_string: str) -> list[str]:
        tokenizer = Tokenizer(func_content, file_path_str,
                              line=line, col=col, file_string=file_string)
        programs = tokenizer.programs
        return self._parse_func_content(tokenizer, programs, is_load=False)

    def _parse_func_content(self, tokenizer: Tokenizer, programs: list[list[Token]], is_load: bool) -> list[str]:

        command_strings: list[str] = []
        commands: list[str] = []
        """List of argument in a line of command"""

        for command in programs:
            if command[0].token_type != TokenType.keyword:
                raise JMCSyntaxException(
                    "Expected keyword", command[0], tokenizer)
            elif command[0].string == 'new':
                raise JMCSyntaxException(
                    "'new' keyword found in function", command[0], tokenizer)
            elif command[0].string == 'class':
                raise JMCSyntaxException(
                    "'class' keyword found in function", command[0], tokenizer)
            elif command[0].string == 'function' and len(command) == 4:
                raise JMCSyntaxException(
                    "Function declaration found in function", command[0], tokenizer)
            elif command[0].string == '@import':
                raise JMCSyntaxException(
                    "Importing found in function", command[0], tokenizer)

            # Boxes check
            if self.do_while_box is not None:
                if command[0].string != 'while':
                    raise JMCSyntaxException(
                        "Expected 'while'", command[0], tokenizer)
            if self.if_else_box:
                if command[0].string != 'else':
                    append_commands(commands, self.parse_if_else(tokenizer))

            if commands:
                command_strings.append(' '.join(commands))
                commands = []
            is_expect_command = True
            is_execute = (command[0].string == 'execute')

            for key_pos, token in enumerate(command):
                if is_expect_command:
                    is_expect_command = False
                    # Handle Errors
                    if token.token_type != TokenType.keyword:
                        if token.token_type == TokenType.paren_curly and is_execute:
                            append_commands(commands, self.datapack.add_private_function(
                                'anonymous', token, tokenizer))
                            break
                        else:
                            raise JMCSyntaxException(
                                "Expected keyword", token, tokenizer)

                    # End Handle Errors

                    if is_number(token.string) and key_pos == 0:
                        if len(command[key_pos:]) > 1:
                            raise JMCSyntaxException(
                                "Unexpected token", command[key_pos+1], tokenizer, display_col_length=False)

                        if not command_strings:
                            raise JMCSyntaxException(
                                "Expected command, got number", token, tokenizer, display_col_length=False)

                        is_break = False
                        if not command_strings[-1].startswith('execute'):
                            for _cmd in ALLOW_NUMBER_AFTER:
                                if command_strings[-1].startswith(_cmd):
                                    command_strings[-1] += ' '+token.string
                                    is_break = True
                                    break
                            else:
                                raise JMCSyntaxException(
                                    "Unexpected number", token, tokenizer, display_col_length=False)
                        if is_break:
                            break

                        is_break = False
                        for _cmd in ALLOW_NUMBER_AFTER:
                            if _cmd in command_strings[-1]:
                                command_strings[-1] += ' '+token.string
                                is_break = True
                                break
                        else:
                            raise JMCSyntaxException(
                                "Unexpected number", token, tokenizer, display_col_length=False)
                        if is_break:
                            break

                    if token.string == 'say':
                        if len(command[key_pos:]) == 1:
                            raise JMCSyntaxException(
                                "Expected string after 'say' command", token, tokenizer, col_length=True)

                        if command[key_pos+1].token_type != TokenType.string:
                            raise JMCSyntaxException(
                                "Expected string after 'say' command", command[key_pos+1], tokenizer, display_col_length=False, suggestion="(In JMC, you are required to wrapped say command's argument in quote.)")

                        if len(command[key_pos:]) > 2:
                            raise JMCSyntaxException(
                                "Unexpected toke", command[key_pos+2], tokenizer, display_col_length=False)

                        if '\n' in command[key_pos+1].string:
                            raise JMCSyntaxException(
                                "Newline found in say command", command[key_pos+1], tokenizer)
                        append_commands(
                            commands, f"say {command[key_pos+1].string}")
                        break

                    if token.string.startswith(DataPack.VARIABLE_SIGN):
                        if len(command) > key_pos+1 and command[key_pos+1].string == 'run' and command[key_pos+1].token_type == TokenType.keyword:
                            is_execute = True
                            append_commands(commands,
                                            f"execute store result score {token.string} {DataPack.VAR_NAME}")
                            continue

                        else:
                            append_commands(commands, variable_operation(
                                command[key_pos:], tokenizer, self.datapack))
                            break

                    matched_function = LOAD_ONCE_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) cannot be used with 'execute'", token, tokenizer)
                        if token.string in self.datapack.used_command:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) can only be used once per datapack", token, tokenizer)
                        if not is_load:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) can only be used in load function", token, tokenizer)

                        self.datapack.used_command.add(token.string)
                        append_commands(commands, matched_function(
                            command[key_pos+1], self.datapack, tokenizer).call())
                        break

                    matched_function = EXECUTE_EXCLUDED_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) cannot be used with 'execute'", token, tokenizer)
                        self.datapack.used_command.add(token.string)
                        append_commands(commands, matched_function(
                            command[key_pos+1], self.datapack, tokenizer))
                        break

                    matched_function = LOAD_ONLY_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) cannot be used with 'execute'", token, tokenizer)
                        if not is_load:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) can only be used in load function", token, tokenizer)
                        append_commands(commands, matched_function(
                            command[key_pos+1], self.datapack, tokenizer))
                        break

                    matched_function = FLOW_CONTROL_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) cannot be used with 'execute'", token, tokenizer)
                        return_value = matched_function(
                            command[key_pos:], self.datapack, tokenizer)
                        if return_value is not None:
                            append_commands(commands, return_value)
                        break

                    matched_function = JMC_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if len(command) > key_pos+2:
                            raise JMCSyntaxException(
                                "Unexpected token", command[key_pos+2], tokenizer, display_col_length=False)
                        append_commands(commands, matched_function(
                            command[key_pos+1], self.datapack, tokenizer, is_execute).call())
                        break

                    if token.string in BOOL_FUNCTIONS:
                        raise JMCSyntaxException(
                            f"This feature({token.string}) only works in JMC's custom condition", token, tokenizer)

                    if token.string in {'new', 'class' '@import'} or (
                        token.string == 'function' and
                        len(command) > key_pos + 2
                    ):
                        if is_execute:
                            raise JMCSyntaxException(
                                f"This feature({token.string}) can only be used in load function", token, tokenizer)
                    if len(command[key_pos:]) == 2 and command[key_pos+1].token_type == TokenType.paren_round:
                        if command[key_pos+1].string != '()':
                            raise JMCSyntaxException(
                                "Custom function's parameter is not supported.\nExpected empty bracket", command[key_pos+1], tokenizer)
                        append_commands(commands,
                                        f"function {self.datapack.namespace}:{token.string.lower().replace('.','/')}")
                        break

                    if token.string in VANILLA_COMMANDS:
                        append_commands(commands, token.string)
                    else:
                        raise JMCSyntaxException(
                            f"Unrecognized command", token, tokenizer)

                else:
                    if token.string == 'run' and token.token_type == TokenType.keyword:
                        if not is_execute:
                            raise MinecraftSyntaxWarning(
                                "'run' keyword found outside 'execute' command", token, tokenizer)
                        is_expect_command = True
                    if (
                        token.token_type == TokenType.keyword and
                        token.string in FIRST_ARGUMENTS and
                        not (
                            token.string == 'function' and
                            commands[-1] == 'schedule'
                        )
                    ):
                        raise JMCSyntaxException(
                            f"Keyword({token.string}) at line {token.line} col {token.col} is recognized as a command.\nExpected semicolon(;)", command[key_pos-1], tokenizer, col_length=True)

                    if token.string == '@s' and token.token_type == TokenType.keyword and commands[-1] == 'as':
                        commands[-1] = 'if entity'

                    if token.token_type in {TokenType.paren_curly, TokenType.paren_round, TokenType.paren_square}:
                        if is_connected(token, command[key_pos-1]):
                            commands[-1] += tokenizer.clean_up_paren(token)
                        else:
                            append_commands(commands, tokenizer.clean_up_paren(
                                token))
                    elif token.token_type == TokenType.string:
                        append_commands(commands, dumps(token.string))
                    else:
                        append_commands(commands, token.string)

        # End of Program

        # Boxes check
        if self.do_while_box is not None:
            raise JMCSyntaxException(
                "Expected 'while'", programs[-1][-1], tokenizer)
        if self.if_else_box:
            append_commands(commands, self.parse_if_else(tokenizer))

        if commands:
            command_strings.append(' '.join(commands))
            commands = []
        return command_strings

    def parse_class_content(self, prefix: str, class_content: str, file_path_str: str, line: int, col: int, file_string: str) -> None:
        tokenizer = Tokenizer(class_content, file_path_str,
                              line=line, col=col, file_string=file_string)
        for command in tokenizer.programs:
            if command[0].string == 'function' and len(command) == 4:
                self.parse_func(tokenizer, command, file_path_str, prefix)
            elif command[0].string == 'new':
                self.parse_new(tokenizer, command, file_path_str, prefix)
            elif command[0].string == 'class':
                self.parse_class(tokenizer, command, file_path_str, prefix)
            elif command[0].string == '@import':
                raise JMCSyntaxException(
                    "Importing is not supported in class", command[0], tokenizer)
            else:
                raise JMCSyntaxException(
                    f"Expected 'function' or 'new' or 'class' (got {command[0].string})", command[0], tokenizer)

    def parse_if_else(self, tokenizer: Tokenizer) -> str:
        VAR = "__if_else__"
        NAME = "if_else"

        logger.debug("Handling if-else")
        if_else_box = self.if_else_box
        self.if_else_box = []
        condition, precommand = parse_condition(
            if_else_box[0][0], tokenizer, self.datapack)
        # Case 1: `if` only
        if len(if_else_box) == 1:
            return_value = f"{precommand}execute {condition} run {self.datapack.add_private_function(NAME, if_else_box[0][1], tokenizer)}"
            return return_value

        # Case 2
        count = self.datapack.get_count(NAME)
        count_alt = self.datapack.get_count(NAME)
        output = [
            f"scoreboard players set {VAR} {DataPack.VAR_NAME} 0",
            f"{precommand}execute {condition} run {self.datapack.add_custom_private_function(NAME, if_else_box[0][1], tokenizer, count, postcommands=[f'scoreboard players set {VAR} {DataPack.VAR_NAME} 1'])}",
            f"execute if score {VAR} {DataPack.VAR_NAME} matches 0 run function {self.datapack.namespace}:{DataPack.PRIVATE_NAME}/{VAR}/{count_alt}"]
        del if_else_box[0]

        if if_else_box[-1][0] is None:
            else_ = if_else_box[-1][1]
            del if_else_box[-1]
        else:
            else_ = None

        # `else if`
        if if_else_box:
            for else_if in if_else_box:
                condition, precommand = parse_condition(
                    else_if[0], tokenizer, self.datapack)
                count = self.datapack.get_count(NAME)
                count_tmp = count_alt
                count_alt = self.datapack.get_count(NAME)

                self.datapack.add_raw_private_function(NAME, [
                    f"{precommand}execute {condition} run function {self.datapack.namespace}:{DataPack.PRIVATE_NAME}/{VAR}/{count}",
                    f"execute if score {VAR} {DataPack.VAR_NAME} matches 0 run function {self.datapack.namespace}:{DataPack.PRIVATE_NAME}/{VAR}/{count_alt}"
                ], count_tmp)

                self.datapack.add_custom_private_function(NAME, else_if[1], tokenizer, count, postcommands=[
                    f"scoreboard players set {VAR} {DataPack.VAR_NAME} 1"
                ])
        # `else`
        if else_ is None:
            self.datapack.private_functions[NAME][count_tmp].delete(-1)
        else:
            self.datapack.add_custom_private_function(
                NAME, else_, tokenizer, count_alt)
        return "\n".join(output)
