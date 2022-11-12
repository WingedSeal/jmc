"""Module responsible for handling all Function Content parsing in Lexer"""
from typing import TYPE_CHECKING
from json import dumps

from .vanilla_command import COMMANDS as VANILLA_COMMANDS
from .tokenizer import Tokenizer, Token, TokenType
from .exception import JMCSyntaxException, MinecraftSyntaxWarning
from .log import Logger
from .utils import convention_jmc_to_mc, is_number, is_connected, search_to_string
from .datapack import DataPack
from .command.condition import BOOL_FUNCTIONS
from .command import (FLOW_CONTROL_COMMANDS,
                      variable_operation,
                      JMCFunction,
                      FuncType,
                      JMCFunction,
                      )

if TYPE_CHECKING:
    from .lexer import Lexer

logger = Logger(__name__)

EXECUTE_EXCLUDED_COMMANDS = JMCFunction.get_subclasses(
    FuncType.EXECUTE_EXCLUDED)
"""Dictionary of command's name and a class of JMCFunction type for custom jmc command that can't be used with `/execute`"""
LOAD_ONCE_COMMANDS = JMCFunction.get_subclasses(FuncType.LOAD_ONCE)
"""Dictionary of command's name and a class of JMCFunction type for custom jmc command that can be only used *once* in load"""
JMC_COMMANDS = JMCFunction.get_subclasses(FuncType.JMC_COMMAND)
"""Dictionary of command's name and a class of JMCFunction type for custom jmc command"""
LOAD_ONLY_COMMANDS = JMCFunction.get_subclasses(FuncType.LOAD_ONLY)
"""Dictionary of command's name and a class of JMCFunction type for custom jmc command that can only be used in load"""

FIRST_ARGUMENTS = {
    *FLOW_CONTROL_COMMANDS,
    *LOAD_ONCE_COMMANDS,
    *LOAD_ONLY_COMMANDS,
    *JMC_COMMANDS,
    *FLOW_CONTROL_COMMANDS,
    *EXECUTE_EXCLUDED_COMMANDS,
    *VANILLA_COMMANDS
} - {'give', 'if'}
"""Set of all vanilla commands and JMC custom syntax
- `if` is excluded since it can be used in execute
- `give` is exluced since it can also be arguments (`/effect give`)"""

ALLOW_NUMBER_AFTER = [
    'give',
    'clear'
]
"""List of vanilla command to stop JMC from terminating line from curly parenthesis (Allow number after curly parenthesis)"""


def append_commands(commands: list[str], string: str) -> None:
    """
    Append a new argument to a comand(list of minecraft arguments) while optimizing it

    :param commands: Entire command(list of minecraft arguments) to add to
    :param string: A new argument to add
    """
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


class FuncContent:
    """
    A class representation of a row function for parsing content inside the function

    :param tokenizer: Tokenizer
    :param programs: List of commands(List of arguments(Token))
    :param is_load: Whether the function is a load function
    """
    __slots__ = 'tokenizer', 'programs', 'is_load', 'command_strings', 'commands', 'command', 'is_expect_command', 'is_execute', 'lexer'

    command: list[Token]
    is_expect_command: bool
    is_execute: bool

    def __init__(self, tokenizer: Tokenizer,
                 programs: list[list[Token]], is_load: bool, lexer: "Lexer") -> None:

        self.tokenizer = tokenizer
        self.programs = programs
        self.is_load = is_load
        self.command_strings: list[str] = []
        self.commands: list[str] = []
        self.lexer = lexer

    def parse(self) -> list[str]:
        """
        Parse the content
        :return: List of commands(String)
        """
        for command in self.programs:
            self.command = command
            if self.command[0].token_type != TokenType.KEYWORD:
                raise JMCSyntaxException(
                    "Expected keyword", self.command[0], self.tokenizer)
            elif self.command[0].string == 'new':
                raise JMCSyntaxException(
                    "'new' keyword found in function", self.command[0], self.tokenizer)
            elif self.command[0].string == 'class':
                raise JMCSyntaxException(
                    "'class' keyword found in function", self.command[0], self.tokenizer)
            elif self.command[0].string == 'function' and len(self.command) == 4:
                raise JMCSyntaxException(
                    "Function declaration found in function", self.command[0], self.tokenizer)
            elif self.command[0].string == '@import':
                raise JMCSyntaxException(
                    "Importing found in function", self.command[0], self.tokenizer)

            # Boxes check
            if self.lexer.do_while_box is not None:
                if self.command[0].string != 'while':
                    raise JMCSyntaxException(
                        "Expected 'while'", self.command[0], self.tokenizer)
            if self.lexer.if_else_box:
                if self.command[0].string != 'else':
                    append_commands(
                        self.commands, self.lexer.parse_if_else(
                            self.tokenizer))

            if self.commands:
                self.command_strings.append(' '.join(self.commands))
                self.commands = []

            self.parse_commands()
        # End of Program

        # Boxes check
        if self.lexer.do_while_box is not None:
            raise JMCSyntaxException(
                "Expected 'while'", self.programs[-1][-1], self.tokenizer)
        if self.lexer.if_else_box:
            append_commands(
                self.commands,
                self.lexer.parse_if_else(
                    self.tokenizer))

        if self.commands:
            self.command_strings.append(' '.join(self.commands))
            self.commands = []
        return self.command_strings

    def parse_commands(self) -> None:
        self.is_expect_command = True
        self.is_execute = (self.command[0].string == 'execute')

        for key_pos, token in enumerate(self.command):
            if not self.is_expect_command:
                self._not_expect_command(key_pos, token)
                continue
            if self._expect_command(key_pos, token):
                break

    def _not_expect_command(self, key_pos: int, token: Token) -> None:
        if token.string == 'run' and token.token_type == TokenType.KEYWORD:
            if not self.is_execute:
                raise MinecraftSyntaxWarning(
                    "'run' keyword found outside 'execute' command", token, self.tokenizer)
            self.is_expect_command = True

        if (
            token.token_type == TokenType.KEYWORD and
            token.string in FIRST_ARGUMENTS and
            not (
                token.string == 'function' and
                self.commands[-1] == 'schedule'
            )
        ):
            raise JMCSyntaxException(
                f"Keyword({token.string}) at line {token.line} col {token.col} is recognized as a command.\nExpected semicolon(;)", self.command[key_pos - 1], self.tokenizer, col_length=True)

        # optimize `execute as @s`
        if (token.string == '@s' and
            token.token_type == TokenType.KEYWORD and
            self.commands[-1] == 'as' and
                self.commands[-2] not in {'rotated', 'positioned'}):

            self.commands[-1] = 'if entity'

        if token.token_type == TokenType.PAREN_ROUND:
            self.commands[-1], success = search_to_string(
                self.commands[-1], token, DataPack.var_name, self.tokenizer)
            if not success:
                if is_connected(token, self.command[key_pos - 1]):
                    self.commands[-1] += self.lexer.clean_up_paren_token(
                        token, self.tokenizer)
                else:
                    append_commands(
                        self.commands, self.lexer.clean_up_paren_token(token, self.tokenizer))
        elif token.token_type in {TokenType.PAREN_CURLY, TokenType.PAREN_SQUARE}:
            if is_connected(token, self.command[key_pos - 1]):
                self.commands[-1] += self.lexer.clean_up_paren_token(
                    token, self.tokenizer)
            else:
                append_commands(
                    self.commands, self.lexer.clean_up_paren_token(token, self.tokenizer))
        elif token.token_type == TokenType.STRING:
            append_commands(self.commands, dumps(token.string))
        else:
            append_commands(self.commands, token.string)

    def _expect_command(self, key_pos: int, token: Token) -> bool:
        self.is_expect_command = False
        # Handle Errors
        if token.token_type != TokenType.KEYWORD:
            if token.token_type == TokenType.PAREN_CURLY and self.is_execute:
                append_commands(self.commands, self.lexer.datapack.add_arrow_function(
                    'anonymous', token, self.tokenizer))
                return True
            else:
                raise JMCSyntaxException(
                    "Expected keyword", token, self.tokenizer)

        # End Handle Errors

        if is_number(token.string) and key_pos == 0:
            self.__is_number(key_pos, token)
            return True

        if token.string == 'say':
            self.__is_say(key_pos, token)
            return True

        if token.string.startswith(DataPack.VARIABLE_SIGN):
            if self.__is_startswith_varsign(key_pos, token):
                return True

        if self.__is_jmc_function(key_pos, token):
            if len(self.command[key_pos:]) > 2:
                raise JMCSyntaxException(
                    f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True)
            return True

        if self.__is_flow_control_command(key_pos, token):
            return True

        if token.string in {'new', 'class' '@import'} or (
            token.string == 'function'
            and
            len(self.command) > key_pos + 2
        ):
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) can only be used in load function", token, self.tokenizer)
        if len(self.command[key_pos:]) >= 2 and self.command[key_pos +
                                                             1].token_type == TokenType.PAREN_ROUND:
            if len(self.command[key_pos:]) > 2:
                raise JMCSyntaxException(
                    f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True)

            if self.command[key_pos + 1].string != '()':
                raise JMCSyntaxException(
                    f"Custom function({token.string})'s parameter is not supported.\nExpected empty bracket", self.command[key_pos + 1], self.tokenizer)
            append_commands(self.commands,
                            f"function {self.lexer.datapack.namespace}:{convention_jmc_to_mc(token, self.tokenizer)}")
            return True

        if token.string not in VANILLA_COMMANDS:
            raise JMCSyntaxException(
                f"Unrecognized command ({token.string})", token, self.tokenizer)

        append_commands(self.commands, token.string)
        return False

    def __is_number(self, key_pos: int, token: Token) -> None:
        if len(self.command[key_pos:]) > 1:
            raise JMCSyntaxException(
                "Unexpected token", self.command[key_pos + 1], self.tokenizer, display_col_length=False)

        if not self.command_strings:
            raise JMCSyntaxException(
                "Expected command, got number", token, self.tokenizer, display_col_length=False)

        if not self.command_strings[-1].startswith('execute'):
            for _cmd in ALLOW_NUMBER_AFTER:
                if self.command_strings[-1].startswith(_cmd):
                    self.command_strings[-1] += ' ' + token.string
                    return
            raise JMCSyntaxException(
                "Unexpected number", token, self.tokenizer, display_col_length=False)

        for _cmd in ALLOW_NUMBER_AFTER:
            if _cmd in self.command_strings[-1]:
                self.command_strings[-1] += ' ' + token.string
                return

        raise JMCSyntaxException(
            "Unexpected number", token, self.tokenizer, display_col_length=False)

    def __is_say(self, key_pos: int, token: Token) -> None:
        if len(self.command[key_pos:]) == 1:
            raise JMCSyntaxException(
                "Expected string after 'say' command", token, self.tokenizer, col_length=True)

        if self.command[key_pos + 1].token_type != TokenType.STRING:
            raise JMCSyntaxException(
                "Expected string after 'say' command", self.command[key_pos + 1], self.tokenizer, display_col_length=False, suggestion="(In JMC, you are required to wrapped say command's argument in quote.)")

        if len(self.command[key_pos:]) > 2:
            raise JMCSyntaxException(
                "Unexpected token", self.command[key_pos + 2], self.tokenizer, display_col_length=False)

        if '\n' in self.command[key_pos + 1].string:
            raise JMCSyntaxException(
                "Newline found in say command", self.command[key_pos + 1], self.tokenizer, suggestion=r"Use '\\n' instead of '\n'")
        append_commands(
            self.commands, f"say {self.command[key_pos+1].string}")

    def __is_startswith_varsign(self, key_pos: int, token: Token) -> bool:
        if len(
                self.command) > key_pos + 1 and self.command[key_pos + 1].string == 'run' and self.command[key_pos + 1].token_type == TokenType.KEYWORD:
            self.is_execute = True
            append_commands(self.commands,
                            f"execute store result score {token.string} {DataPack.var_name}")
            return False

        else:
            append_commands(self.commands, variable_operation(
                self.command[key_pos:], self.tokenizer, self.lexer.datapack, self.is_execute))
            return True

    def __is_jmc_function(self, key_pos: int, token: Token) -> bool:
        load_once_command = self.get_function(token, LOAD_ONCE_COMMANDS)
        if load_once_command is not None:
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) cannot be used with 'execute'", token, self.tokenizer)
            if token.string in self.lexer.datapack.used_command:
                raise JMCSyntaxException(
                    f"This feature({token.string}) can only be used once per datapack", token, self.tokenizer)
            if not self.is_load:
                raise JMCSyntaxException(
                    f"This feature({token.string}) can only be used in load function", token, self.tokenizer)

            self.lexer.datapack.used_command.add(token.string)
            append_commands(self.commands, load_once_command(
                self.command[key_pos + 1], self.lexer.datapack, self.tokenizer).call())
            return True

        execute_excluded_command = self.get_function(
            token, EXECUTE_EXCLUDED_COMMANDS)
        if execute_excluded_command is not None:
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) cannot be used with 'execute'", token, self.tokenizer)
            self.lexer.datapack.used_command.add(token.string)
            append_commands(self.commands, execute_excluded_command(
                self.command[key_pos + 1], self.lexer.datapack, self.tokenizer).call())
            return True

        load_only_command = self.get_function(token, LOAD_ONLY_COMMANDS)
        if load_only_command is not None:
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) cannot be used with 'execute'", token, self.tokenizer)
            if not self.is_load:
                raise JMCSyntaxException(
                    f"This feature({token.string}) can only be used in load function", token, self.tokenizer)
            append_commands(self.commands, load_only_command(
                self.command[key_pos + 1], self.lexer.datapack, self.tokenizer).call())
            return True

        jmc_command = self.get_function(token, JMC_COMMANDS)
        if jmc_command is not None:
            if len(self.command) > key_pos + 2:
                raise JMCSyntaxException(
                    "Unexpected token", self.command[key_pos + 2], self.tokenizer, display_col_length=False)
            append_commands(self.commands, jmc_command(
                self.command[key_pos + 1], self.lexer.datapack, self.tokenizer, is_execute=self.is_execute).call())
            return True

        if token.string in BOOL_FUNCTIONS:
            raise JMCSyntaxException(
                f"This feature({token.string}) only works in JMC's custom condition", token, self.tokenizer)

        return False

    def __is_flow_control_command(self, key_pos: int, token: Token) -> bool:
        flow_control_command = FLOW_CONTROL_COMMANDS.get(
            token.string, None)
        if flow_control_command is not None:
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) cannot be used with 'execute'", token, self.tokenizer)
            return_value = flow_control_command(
                self.command[key_pos:], self.lexer.datapack, self.tokenizer)
            if return_value is not None:
                append_commands(self.commands, return_value)
            return True
        return False

    def get_function(self, token: Token,
                     command_functions: dict[str, type["JMCFunction"]]) -> type["JMCFunction"] | None:
        return command_functions.get(token.string, None)
