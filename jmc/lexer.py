from pathlib import Path
from json import loads, JSONDecodeError, dumps
from typing import Optional

from jmc.command.execute_excluded import EXECUTE_EXCLUDED_COMMANDS

from .exception import JMCDecodeJSONError, JMCFileNotFoundError, JMCSyntaxException, JMCSyntaxWarning, MinecraftSyntaxWarning
from .vanilla_command import COMMANDS as VANILLA_COMMANDS
from .tokenizer import Tokenizer, Token, TokenType
from .datapack import DataPack, Function
from .log import Logger
from .command import (LOAD_ONCE_COMMANDS,
                      LOAD_ONLY_COMMANDS,
                      JMC_COMMANDS,
                      FLOW_CONTROL_COMMANDS,
                      variable_operation,
                      parse_condition,
                      )

logger = Logger(__name__)

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

FIRST_ARGUMENTS = [
    *VANILLA_COMMANDS,
    *LOAD_ONCE_COMMANDS,
    *LOAD_ONLY_COMMANDS,
    *JMC_COMMANDS,
    *FLOW_CONTROL_COMMANDS,
    *EXECUTE_EXCLUDED_COMMANDS
]
"""All vanilla commands and JMC custom syntax 

`if` and `else` are excluded from the list since it can be used in execute"""
NEW_LINE = '\n'


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
                        f"In {tokenizer.file_path}\nExpected string after '@import' at line {command[0].line} col {command[0].col+command[0].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length - 1]} <-"
                    )
                if command[1].token_type != TokenType.string:
                    raise JMCSyntaxException(
                        f"In {tokenizer.file_path}\nExpected string after '@import' at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length - 1]} <-"
                    )
                if len(command) > 2:
                    raise JMCSyntaxException(
                        f"In {tokenizer.file_path}\nUnexpected token at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col]} <-"
                    )
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
                        f"In {tokenizer.file_path}\nExpected invalid path ({command[1].string}) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length - 1]} <-"
                    )
                self.parse_file(file_path=new_path)
            else:
                if not is_load:
                    raise JMCSyntaxException(
                        f"In {tokenizer.file_path}\nCommand({command[1].string}) found inside non-load file at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length - 1]} <-"
                    )
                self.datapack.load_function.append(command)

    def parse_func(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = '') -> None:
        logger.debug(f"Parsing function, prefix = {prefix!r}")
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(function's name) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length - 1]} <-"
            )
        elif command[2].string != '()':
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected ( at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col]} <-"
            )
        elif command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[3].line} col {command[3].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[3].line-1][:command[3].col-1]} <-"
            )

        func_path = prefix + command[1].string.lower().replace('.', '/')
        if func_path.startswith(self.datapack.PRIVATE_NAME+'/'):
            raise JMCSyntaxWarning(
                f"In {tokenizer.file_path}\nFunction({func_path}) may override private function of JMC at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1+command[1].length-1]} <-\nPlease avoid starting function's path with {self.datapack.PRIVATE_NAME}"
            )
        logger.debug(f"Function: {func_path}")
        func_content = command[3].string[1:-1]
        if func_path in self.datapack.functions:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nDuplicate function declaration({func_path}) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1+command[1].length-1]} <-"
            )
        elif func_path == self.datapack.LOAD_NAME:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nLoad function is defined at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1]} <-"
            )
        elif func_path == self.datapack.PRIVATE_NAME:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nPrivate function is defined at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1]} <-"
            )
        self.datapack.functions[func_path] = Function(self.parse_func_content(
            func_content, file_path_str, line=command[3].line, col=command[3].col, file_string=tokenizer.file_string))

    def parse_new(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = ''):
        logger.debug(f"Parsing 'new' keyword, prefix = {prefix!r}")
        if len(command) < 2:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(JSON file's type) at line {command[0].line} col {command[0].col +  + command[0].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length - 1]} <-"
            )
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(JSON file's type) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length - 1]} <-"
            )
        if len(command) < 3:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected JSON file's path in bracket at line {command[1].line + command[1].length} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length -1]} <-"
            )
        if command[2].string == '()':
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected JSON file's path in bracket at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col]} <-"
            )
        if command[2].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected ( at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1]} <-"
            )
        if len(command) < 4:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[2].line} col {command[2].col + command[2].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1] + command[2].length -1} <-"
            )
        if command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[3].line} col {command[3].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[3].line-1][:command[3].col-1]} <-"
            )

        json_type = command[1].string.replace('.', '/')
        if json_type not in JSON_FILE_TYPES:
            raise MinecraftSyntaxWarning(
                f"In {tokenizer.file_path}\nUnrecognized JSON file's type({json_type}) at line {command[2].line} col {command[2].col+1}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col+command[2].length-1]} <-\nExample of valid JSON file type: advancements, predicates, etc."
            )
        json_path = json_type + '/' + prefix + \
            command[2].string[1:-1].replace('.', '/')
        if not json_path.islower():
            raise MinecraftSyntaxWarning(
                f"In {tokenizer.file_path}\nUppercase letter found in JSON file's path({json_path}) at line {command[2].line} col {command[2].col+1}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col+command[2].length-1]} <-"
            )
        logger.debug(f"JSON: {json_type}({json_path})")
        json_content = command[3].string
        if json_path in self.datapack.jsons:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nDuplicate JSON({json_path}) at line {command[2].line} col {command[2].col+1}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col+command[2].length-1]} <-"
            )
        try:
            json: dict[str, str] = loads(json_content)
        except JSONDecodeError as error:
            line = command[3].line + error.lineno - 1
            col = command[3].col + error.colno - 1 \
                if command[3].line == line else error.colno
            raise JMCDecodeJSONError(
                f"In {tokenizer.file_path}\n{error.msg} at line {line} col {col}.\n{tokenizer.file_string.split(NEW_LINE)[line-1][:col-1]} <-"
            )
        self.datapack.jsons[json_path] = json

    def parse_class(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = ''):
        logger.debug(f"Parsing Class, prefix = {prefix!r}")
        if len(command) < 2:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(class's name) at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length - 1]} <-"
            )
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(class's name) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length - 1]} <-"
            )
        if len(command) < 3:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[1].line} col {command[1].col+command[1].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col+command[1].length-1]} <-"
            )
        if command[2].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1]} <-"
            )

        class_path = prefix + command[1].string.lower().replace('.', '/')
        class_content = command[2].string[1:-1]
        self.parse_class_content(class_path+'/',
                                 class_content, file_path_str, line=command[2].line, col=command[2].col, file_string=tokenizer.file_string)

    def parse_load_func_content(self, programs: list[list[Token]]):
        tokenizer = self.load_tokenizer
        return self.__parse_func_content(tokenizer, programs, is_load=True)

    def parse_func_content(self,
                           func_content: str, file_path_str: str,
                           line: int, col: int, file_string: str) -> list[str]:
        tokenizer = Tokenizer(func_content, file_path_str,
                              line=line, col=col, file_string=file_string)
        programs = tokenizer.programs
        return self.__parse_func_content(tokenizer, programs, is_load=False)

    def __parse_func_content(self, tokenizer: Tokenizer, programs: list[list[Token]], is_load: bool) -> list[str]:

        command_strings = []
        commands: list[str] = []
        """List of argument in a line of command"""

        for command in programs:
            if command[0].token_type != TokenType.keyword:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nExpected keyword at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col]} <-"
                )
            elif command[0].string == 'new':
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\n'new' keyword found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            elif command[0].string == 'class':
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\n'class' keyword found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            elif command[0].string == 'function' and len(command) == 4:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nFunction declaration found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            elif command[0].string == '@import':
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nImporting found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            # elif command[0].string not in FIRST_ARGUMENTS:
            #     if not (len(command) == 2 and command[1].token_type == TokenType.paren_round):
            #         raise JMCSyntaxException(
            #             f"In {tokenizer.file_path}\nUnrecognized command ({command[0].string}) at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length - 1]} <-"
            #         )

            # Boxes check
            if self.do_while_box is not None:
                if command[0].string != 'while':
                    raise JMCSyntaxException(
                        f"In {tokenizer.file_path}\nExpected 'while' at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col-1]} <-"
                    )
            if self.if_else_box:
                if command[0].string != 'else':
                    commands.append(self.parse_if_else(tokenizer))

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
                            commands.append(self.datapack.add_private_function(
                                'anonymous', token, tokenizer))
                            break
                        else:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nExpected keyword at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                    # End Handle Errors

                    if token.string == 'say':
                        if len(command[key_pos:]) == 1:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nExpected string after 'say' at line {token.line} col {token.col+token.length}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        if command[key_pos+1].token_type != TokenType.string:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nExpected string after 'say' at line {token.line} col {token.col+token.length}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-\n(In JMC, you are required to wrapped say command's argument in quote.)"
                            )
                        if len(command[key_pos:]) > 2:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nUnexpected token at line {command[key_pos+2].line} col {command[key_pos+2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[key_pos+2].line-1][:command[key_pos+2].col]} <-"
                            )
                        if '\n' in command[key_pos+1].string:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nNewline found in say command at line {command[key_pos+1].line} col {command[key_pos+1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[key_pos+1].line-1][:command[key_pos+1].col+command[key_pos+1].string.find(NEW_LINE)+2]} <-"
                            )
                        commands.append(f"say {command[key_pos+1].string}")
                        break

                    if token.string.startswith(DataPack.VARIABLE_SIGN):
                        if len(command[key_pos:]) == 1:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nExpected operator after variable at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-")

                        if command[key_pos+1].string == 'run' and command[key_pos+1].token_type == TokenType.keyword:
                            is_execute = True
                            commands.append(
                                f"execute store result score {token.string} {DataPack.VAR_NAME}")
                            continue

                        else:
                            commands.append(variable_operation(
                                command[key_pos:], tokenizer, self.datapack))
                            break

                    matched_function = LOAD_ONCE_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature cannot be used with 'execute' at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        if token.string in self.datapack.used_command:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature only be used once per datapack at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        if not is_load:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature only be used in load function at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        self.datapack.used_command.add(token.string)
                        commands.append(matched_function(
                            tokenizer.parse_func_args(command[key_pos+1]), self.datapack, tokenizer))
                        break

                    matched_function = EXECUTE_EXCLUDED_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature cannot be used with 'execute' at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        self.datapack.used_command.add(token.string)
                        commands.append(matched_function(
                            tokenizer.parse_func_args(command[key_pos+1]), self.datapack, tokenizer))
                        break

                    matched_function = LOAD_ONLY_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature({token.string}) cannot be used with 'execute' at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        if not is_load:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature only be used in load function at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        commands.append(matched_function(
                            tokenizer.parse_func_args(command[key_pos+1]), self.datapack, tokenizer))
                        break

                    matched_function = FLOW_CONTROL_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if is_execute:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature({token.string}) cannot be used with 'execute' at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                        return_value = matched_function(
                            command[key_pos:], self.datapack, tokenizer)
                        if return_value is not None:
                            commands.append(return_value)
                        break

                    matched_function = JMC_COMMANDS.get(
                        token.string, None)
                    if matched_function is not None:
                        if len(command) > key_pos+1:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nUnexpected token at line {command[key_pos+2].line} col {command[key_pos+2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[key_pos+2].line-1][:command[key_pos+2].col]} <-"
                            )
                        commands.append(matched_function(
                            tokenizer.parse_func_args(command[key_pos+1]), self.datapack, tokenizer, is_execute))
                        break

                    if token.string in ['new', 'class' '@import'] or (
                        token.string == 'function' and
                        len(command) > key_pos + 2
                    ):
                        if is_execute:
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nThis feature cannot be used with 'execute' at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-"
                            )
                    if len(command[key_pos:]) == 2 and command[key_pos+1].token_type == TokenType.paren_round:
                        if command[key_pos+1].string != '()':
                            raise JMCSyntaxException(
                                f"In {tokenizer.file_path}\nCustom function's parameter is not supported.\nExpected empty bracket at line {command[key_pos+1].line} col {command[key_pos+1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[key_pos+1].line-1][:command[key_pos+1].col + command[key_pos+1].length - 1]} <-"
                            )
                        commands.append(
                            f"function {self.datapack.namespace}:{token.string.lower().replace('.','/')}")
                        break

                    if token.token_type in [TokenType.paren_curly, TokenType.paren_round, TokenType.paren_square]:
                        commands.append(tokenizer.clean_up_paren(
                            token))
                    else:
                        commands.append(token.string)

                else:
                    if token.string == 'run' and is_execute:
                        is_expect_command = True
                    if (
                        token.token_type == TokenType.keyword and
                        token.string in FIRST_ARGUMENTS
                    ):
                        col = command[key_pos-1].col+command[key_pos-1].length
                        raise JMCSyntaxException(
                            f"In {tokenizer.file_path}\nKeyword({token.string}) at line {token.line} col {token.col} is recognized as a command.\nExpected semicolon(;) at line {command[key_pos-1].line} col {col}\n{tokenizer.file_string.split(NEW_LINE)[command[key_pos-1].line-1][:col-1]} <-"
                        )

                    if token.token_type in [TokenType.paren_curly, TokenType.paren_round]:
                        commands.append(tokenizer.clean_up_paren(
                            token))
                    elif token.token_type == TokenType.paren_square:
                        if (
                            # commands[-1] in ['@a', '@e', '@s', '@r', '@p'] and
                            command[key_pos-1].line == token.line and
                            command[key_pos-1].col +
                                command[key_pos-1].length == token.col
                        ):
                            commands[-1] += tokenizer.clean_up_paren(token)
                        else:
                            commands.append(tokenizer.clean_up_paren(
                                token))
                    elif token.token_type == TokenType.string:
                        commands.append(dumps(token.string))
                    else:
                        commands.append(token.string)

        # End of Program

        # Boxes check
        if self.do_while_box is not None:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected 'while' at line {programs[-1][-1].line} col {programs[-1][-1].col}.\n{tokenizer.file_string.split(NEW_LINE)[programs[-1][-1].line-1][:programs[-1][-1].col+programs[-1][-1].length-1]} <-"
            )
        if self.if_else_box:
            commands.append(self.parse_if_else(tokenizer))

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
                    f"In {tokenizer.file_path}\nImporting is not supporteed in class at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            else:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nExpected 'function' or 'new' or 'class' (got {command[0].string}) at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )

    def parse_if_else(self, tokenizer: Tokenizer) -> str:
        VAR = "__if_else__"
        NAME = "if_else"

        logger.debug("Handling if-else")
        if_else_box = self.if_else_box
        self.if_else_box = []
        condition, precommand = parse_condition(
            if_else_box[0][0], tokenizer)
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
                    else_if[0], tokenizer)
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
