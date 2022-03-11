from pathlib import Path
from json import loads, JSONDecodeError

from .exception import JMCDecodeJSONError, JMCFileNotFoundError, JMCSyntaxException
from .vanilla_command import COMMANDS
from .tokenizer import Tokenizer, Token, TokenType
from .datapack import DataPack, Function
from .log import Logger
from .command import BUILT_IN_FUNCTIONS, FLOW_CONTROLS

logger = Logger(__name__)


FIRST_ARGUMENTS = [
    *COMMANDS,
    *BUILT_IN_FUNCTIONS,
    *FLOW_CONTROLS
]
FIRST_ARGUMENTS.remove('if')
"""All vanilla commands and JMC custom syntax 

`if` is excluded from the list since it can be used in execute"""
NEW_LINE = '\n'


class Lexer:
    def __init__(self, config: dict[str, str]) -> None:
        logger.debug("Initializing Lexer")
        self.config = config
        self.datapack = DataPack(config["namespace"])
        self.parse_file(Path(self.config["target"]))

    def parse_file(self, file_path: Path) -> None:
        logger.info(f"Parsing file: {file_path}")
        file_path_str = file_path.resolve().as_posix()
        try:
            with file_path.open('r') as file:
                raw_string = file.read()
        except FileNotFoundError:
            raise JMCFileNotFoundError(
                f"JMC file not found: {file_path.resolve().as_posix()}")
        tokenizer = Tokenizer(raw_string, file_path_str)

        for command in tokenizer.programs:
            if command[0].string == 'function' and len(command) == 4:
                self.parse_func(tokenizer, command, file_path_str)
            elif command[0].string == 'new':
                self.parse_new(tokenizer, command, file_path_str)
            elif command[0].string == 'class':
                self.parse_class(tokenizer, command, file_path_str)
            elif command[0].string == '@import':
                if len(command) != 2:
                    raise JMCSyntaxException(
                        f"In {tokenizer.file_path}\nExpected 1 arguments after '@import' (got {len(command)-1}) at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length]} <-"
                    )
                if command[1].token_type != TokenType.string:
                    raise JMCSyntaxException(
                        f"In {tokenizer.file_path}\nExpected string after '@import' at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length]} <-"
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
                        f"In {tokenizer.file_path}\nExpected invalid path ({command[1].string}) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length]} <-"
                    )
                self.parse_file(file_path=new_path)
            elif command[0].string in COMMANDS:
                self.datapack.load_function.extend(command)
            elif command[0].string in BUILT_IN_FUNCTIONS:
                self.datapack.load_function.extend(command)
            elif command[0].string in FLOW_CONTROLS:
                self.datapack.load_function.extend(command)

    def parse_func(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = '') -> None:
        logger.debug(f"Parsing function, prefix = {prefix!r}")
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(function's name) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length]} <-"
            )
        elif command[2].string != '()':
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected () at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col]} <-"
            )
        elif command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[3].line} col {command[3].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[3].line-1][:command[3].col-1]} <-"
            )

        func_path = prefix + command[1].string
        logger.debug(f"Function: {func_path}")
        func_content = command[3].string[1:-1]
        if func_path in self.datapack.functions:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nDuplicate function declaration({func_path}) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1+command[1].length]} <-"
            )
        elif func_path == self.datapack.LOAD_NAME:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nLoad function is defined at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1]} <-"
            )
        elif func_path == self.datapack.PRIVATE_STR:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nPrivate function is defined at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1]} <-"
            )
        self.datapack.functions[func_path] = self.parse_func_content(
            func_content, file_path_str, line=command[3].line, col=command[3].col, file_string=tokenizer.file_string)

    def parse_new(self, tokenizer: Tokenizer, command: list[Token], file_path_str: str, prefix: str = ''):
        logger.debug(f"Parsing 'new' keyword, prefix = {prefix!r}")
        if len(command) != 4:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected 3 arguments after 'new' (got {len(command)-1}) at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length]} <-"
            )
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(json file's type) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length]} <-"
            )
        elif command[2].string == '()':
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected json file's path in bracket at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col]} <-"
            )
        elif command[2].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected ( at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1]} <-"
            )
        elif command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[3].line} col {command[3].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[3].line-1][:command[3].col-1]} <-"
            )

        json_type = command[1].string
        json_path = json_type + '/' + prefix + command[2].string[1:-1]
        logger.debug(f"JSON: {json_type}({json_path})")
        json_content = command[3].string
        if json_path in self.datapack.jsons:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nDuplicate json({json_path}) at line {command[2].line} col {command[2].col+1}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1+command[2].length]} <-"
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
        if len(command) != 3:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected 2 arguments after 'class' (got {len(command)-1}) at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length]} <-"
            )
        if command[1].token_type != TokenType.keyword:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected keyword(class's name) at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col + command[1].length]} <-"
            )
        elif command[2].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1]} <-"
            )

        class_path = prefix + command[1].string
        class_content = command[2].string[1:-1]
        self.parse_class_content(class_path+'.',
                                 class_content, file_path_str, line=command[2].line, col=command[2].col, file_string=tokenizer.file_string)

    def parse_func_content(self, func_content: str, file_path_str: str, line: int, col: int, file_string: str, is_load=False) -> Function:
        tokenizer = Tokenizer(func_content, file_path_str,
                              line=line, col=col, file_string=file_string)
        command_strings = []
        for command in tokenizer.programs:
            if command[0].string == 'new':
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\n'new' keyword found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            elif command[0].string == 'class':
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\n'class' keyword found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            elif command[0].string == 'function' and len(command) == 4:
                print(tokenizer.file_string)
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nFunction declaration found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )
            elif command[0].string == '@import':
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nImporting found in function at line {command[0].line} col {command[0].col}\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
                )

            command_str = ""
            is_expect_command = True
            is_execute = (command[0].string == 'execute')
            for key_pos, token in enumerate(command):
                if is_expect_command:
                    is_expect_command = False
                    if token.token_type != TokenType.keyword:
                        raise JMCSyntaxException(
                            f"In {tokenizer.file_path}\nExpected keyword at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[command[key_pos].line-1][:token.col + token.length]} <-"
                        )
                    # TODO: PARSE FUNC
                    if token.string in BUILT_IN_FUNCTIONS:
                        pass
                else:
                    if command == 'run' and is_execute:
                        is_expect_command = True
                    if (
                        token.token_type == TokenType.keyword and
                        token.string in FIRST_ARGUMENTS
                    ):
                        col = command[key_pos-1].col+command[key_pos-1].length
                        raise JMCSyntaxException(
                            f"In {tokenizer.file_path}\nKeyword({token.string}) at line {token.line} col {token.col} is regonized as a command.\nExpected semicolon(;) at line {command[key_pos-1].line} col {col}\n{tokenizer.file_string.split(NEW_LINE)[command[key_pos-1].line-1][:col-1]} <-"
                        )

        return Function(command_strings)

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
