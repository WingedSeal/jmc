"""Module responsible for handling all Function Content parsing in Lexer"""
from typing import TYPE_CHECKING
from json import dumps


from .vanilla_command import COMMANDS as VANILLA_COMMANDS
from .tokenizer import Tokenizer, Token, TokenType
from .exception import JMCSyntaxException, MinecraftSyntaxWarning
from .log import Logger
from .utils import convention_jmc_to_mc, is_decorator, is_number, is_connected, search_to_string
from .datapack import DataPack
from .command.condition import BOOL_FUNCTIONS
from .header import Header
from .command import (FLOW_CONTROL_COMMANDS,
                      variable_operation,
                      JMCFunction,
                      FuncType,
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
    *VANILLA_COMMANDS,
    "class",
    "import",
    "new"
}
"""Set of all vanilla commands and JMC custom syntax"""

FIRST_ARGUMENTS_EXCEPTION = {
    "give": {"effect", "recipe", "give"},
    "clear": {"effect", "schedule"},
    "if": {"execute"},
    "summon": {"execute"},
    "function": {"schedule"},
    "trigger": {"scoreboard"},
    "bossbar": {"execute"},
    "title": {"title"},
    "item": {"summon"},
    "loot": {"loot", "give"},
    "data": {"execute"},
    "playsound": {"weather"},
    "particle": {"item"}
}
"""Dictionary of (FIRST_ARGUMENTS that can also be used as normal argument in a command) and (those commands)

Example: `/effect clear` -> `"clear": {"effect"}`"""


# ALLOW_KEYWORD_AFTER_CURLY_PAREN = {
#     "give",
#     "clear",
#     "setblock"
# }
# """Set of vanilla command to stop JMC from terminating line from curly bracket (Allow number after curly bracket)"""


def append_commands(commands: list[str], string: str) -> None:
    """
    Append a new argument to a comand(list of minecraft arguments)

    :param commands: Entire command(list of minecraft arguments) to add to
    :param string: A new argument to add
    """
    if commands and commands[-1] == "run" and string.startswith("execute "):
        commands[-1] = string[8:]  # len('execute ') = 8
    else:
        commands.append(string)


class FuncContent:
    """
    A class representation of a raw function for parsing content inside the function

    :param tokenizer: Tokenizer
    :param programs: List of commands(List of arguments(Token))
    :param is_load: Whether the function is a load function
    """
    __slots__ = "tokenizer", "programs", "is_load", "command_strings", "__commands", "command", "is_expect_command", "is_execute", "lexer", "expanded_commands"

    command: list[Token]
    is_expect_command: bool
    expanded_commands: list[str] | None
    is_execute: bool

    def __init__(self, tokenizer: Tokenizer,
                 programs: list[list[Token]], is_load: bool, lexer: "Lexer") -> None:

        self.tokenizer = tokenizer
        self.programs = programs
        self.is_load = is_load
        self.command_strings: list[str] = []
        self.__commands: list[str] = []
        self.lexer = lexer
        self.expanded_commands = None

    def parse(self) -> list[str]:
        """
        Parse the content
        :return: List of commands(String)
        """
        for command in self.programs:
            self.command = command
            if self.command[0].token_type != TokenType.KEYWORD:
                raise JMCSyntaxException(
                    f"Expected keyword (got {self.command[0].token_type.value})", self.command[0], self.tokenizer)
            if self.command[0].string == "new":
                raise JMCSyntaxException(
                    "'new' keyword found in function", self.command[0], self.tokenizer)
            if self.command[0].string == "class":
                raise JMCSyntaxException(
                    "'class' keyword found in function", self.command[0], self.tokenizer)
            if self.command[0].string == "function" and len(self.command) == 4:
                raise JMCSyntaxException(
                    "Function declaration found in function", self.command[0], self.tokenizer)
            if is_decorator(self.command[0].string):
                raise JMCSyntaxException(
                    "Decorated function declaration found in function", self.command[0], self.tokenizer)
            if self.command[0].string == "import":
                raise JMCSyntaxException(
                    "Importing found in function", self.command[0], self.tokenizer)

            # Boxes check
            if self.lexer.do_while_box is not None:
                if self.command[0].string != "while":
                    raise JMCSyntaxException(
                        "Expected 'while'", self.command[0], self.tokenizer)
            if self.lexer.if_else_box:
                if self.command[0].string != "else":
                    append_commands(
                        self.__commands, self.lexer.parse_if_else(
                            self.tokenizer))

            if self.__commands:
                if self.expanded_commands is not None:
                    for expanded_command in self.expanded_commands:
                        self.command_strings.append(
                            " ".join(self.__commands) + " " + (expanded_command if "\n" not in expanded_command else self.lexer.datapack.add_private_function('expand', expanded_command)))
                else:
                    self.command_strings.append(" ".join(self.__commands))
                self.__commands = []
                self.expanded_commands = None

            self.__parse_commands()
        # End of Program

        # Boxes check
        if self.lexer.do_while_box is not None:
            raise JMCSyntaxException(
                "Expected 'while'", self.programs[-1][-1], self.tokenizer)
        if self.lexer.if_else_box:
            append_commands(
                self.__commands,
                self.lexer.parse_if_else(
                    self.tokenizer))

        if self.__commands:
            if self.expanded_commands is not None:
                for expanded_command in self.expanded_commands:
                    self.command_strings.append(
                        " ".join(self.__commands) + " " + (expanded_command if "\n" not in expanded_command else self.lexer.datapack.add_private_function('expand', expanded_command)))
            else:
                self.command_strings.append(" ".join(self.__commands))
            self.__commands = []
            self.expanded_commands = None
        return self.command_strings

    def __parse_commands(self) -> None:
        """Parse command in self.commands"""
        self.is_expect_command = True
        self.is_execute = (self.command[0].string == "execute")
        command_pos = None

        for key_pos, token in enumerate(self.command):
            if not self.is_expect_command:
                if command_pos is None:
                    raise ValueError("Unknown command_pos")
                self.__not_expect_command(key_pos, token, command_pos)
                continue
            command_pos = key_pos
            if self.__expect_command(key_pos, token):
                break

    def __optimize(self, token: Token) -> bool:
        """
        Optimize minecraft command by removing redundancy
        :param token: Current token
        :return: Whether to cancel appending this token
        """
        if token.token_type != TokenType.KEYWORD:
            return False
        if not self.__commands:
            return False

        # `execute as @s`
        if (
            token.string == "@s" and
            self.__commands[-1] == "as" and
            self.__commands[-2] not in {"rotated", "positioned"}
        ):

            self.__commands[-1] = "if entity"
            return False

        # `execute run`
        if (
            token.string == "run"
            and self.__commands[-1] == "execute"
        ):
            del self.__commands[-1]
            return True

        # `run execute`
        if (
            token.string == "execute"
            and self.__commands[-1] == "run"
            and self.__commands[0] == "execute"
        ):
            del self.__commands[-1]
            return True

        return False

    def __not_expect_command(
            self, key_pos: int, token: Token, command_pos: int) -> None:
        """
        Called when expecting an argument of command

        :param key_pos: Current index in self.command
        :param token: token
        :param key_pos: Index of latest command in self.command
        :return: Whether to break out of the loop
        """
        if token.string == "run" and token.token_type == TokenType.KEYWORD:
            if not self.is_execute:
                raise MinecraftSyntaxWarning(
                    "'run' keyword found outside 'execute' command", token, self.tokenizer)
            self.is_expect_command = True

        if token.string == "expand" and token.token_type == TokenType.KEYWORD:
            if self.is_execute:
                self.is_expect_command = True
                self.expanded_commands = []

        __is_first_arg = (
            token.string in FIRST_ARGUMENTS
            or
            token.string in Header().commands
            or is_decorator(token.string)
        )
        __is_not_exception = (
            len(self.__commands) > command_pos and
            not (
                token.string in FIRST_ARGUMENTS_EXCEPTION
                and
                self.__commands[command_pos] in FIRST_ARGUMENTS_EXCEPTION[token.string]
            )
        )
        __is_not_connected = not is_connected(token, self.command[key_pos - 1])
        __is_not_deleted = token.string not in Header().dels

        if (
            token.token_type == TokenType.KEYWORD and
            __is_first_arg and
            __is_not_exception and
            __is_not_connected and
            __is_not_deleted
        ):
            raise JMCSyntaxException(
                f"Keyword({token.string}) at line {token.line} col {token.col} is recognized as a command.\nExpected semicolon(;)", self.command[key_pos - 1], self.tokenizer, col_length=True)

        if self.__optimize(token):
            return

        if token.token_type == TokenType.PAREN_ROUND:
            self.__commands[-1], success = search_to_string(
                self.__commands[-1], token, DataPack.var_name, self.tokenizer)
            if not success:
                if is_connected(token, self.command[key_pos - 1]):
                    self.__commands[-1] += self.lexer.clean_up_paren_token(
                        token, self.tokenizer)
                else:
                    append_commands(
                        self.__commands, self.lexer.clean_up_paren_token(token, self.tokenizer))
        elif token.token_type in {TokenType.PAREN_CURLY, TokenType.PAREN_SQUARE}:
            if is_connected(token, self.command[key_pos - 1]):
                self.__commands[-1] += self.lexer.clean_up_paren_token(
                    token, self.tokenizer)
            else:
                append_commands(
                    self.__commands, self.lexer.clean_up_paren_token(token, self.tokenizer))
        elif token.token_type == TokenType.STRING:
            if is_connected(
                    token, self.command[key_pos - 1]) and self.command[key_pos - 1].token_type == TokenType.KEYWORD:
                raise JMCSyntaxException(
                    "Expected whitespace between string and a keyword", self.command[key_pos - 1], self.tokenizer, col_length=True)
            append_commands(self.__commands, dumps(token.string))
        elif (
            token.token_type == TokenType.KEYWORD
            and
            is_connected(token, self.command[key_pos - 1])
            and
            self.command[key_pos - 1].token_type == TokenType.STRING
        ):
            raise JMCSyntaxException(
                "Expected whitespace between string and a keyword", self.command[key_pos - 1], self.tokenizer, col_length=True)
        elif (
            token.token_type in {TokenType.OPERATOR, TokenType.KEYWORD}
            and
            is_connected(token, self.command[key_pos - 1])
        ):
            self.__commands[-1] += token.string
        else:
            append_commands(self.__commands, token.string)

    def __expect_command(self, key_pos: int, token: Token) -> bool:
        """
        Called when expecting a command

        :param key_pos: Current index in self.command
        :param token: token
        :return: Whether to break out of the loop
        """
        self.is_expect_command = False

        # Handle Errors
        if token.token_type != TokenType.KEYWORD:
            if token.token_type == TokenType.PAREN_CURLY and self.is_execute:
                if self.expanded_commands is not None:
                    self.expanded_commands = self.lexer.datapack.parse_function_token(
                        token, self.tokenizer)
                    self.__commands[-1] = "run"
                else:
                    append_commands(self.__commands, self.lexer.datapack.add_arrow_function(
                        "anonymous", token, self.tokenizer))
                return True
            raise JMCSyntaxException(
                "Expected keyword", token, self.tokenizer)

        # End Handle Errors

        if is_number(token.string) and key_pos == 0:
            self.__is_number(key_pos, token)
            return True

        if token.string == "say":
            self.__is_say(key_pos, token)
            return True

        if token.string == "schedule":
            if self.__is_schedule(key_pos):
                return True

        if token.string.startswith(DataPack.VARIABLE_SIGN):
            if self.__is_startswith_var(key_pos):
                return True

        if len(self.command[key_pos:]
               ) > 2 and self.command[key_pos + 1].string == ":":
            if self.__is_startswith_var(key_pos):
                return True

        if self.__is_jmc_function(key_pos, token):
            if len(self.command[key_pos:]) > 2:
                raise JMCSyntaxException(
                    f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True)
            return True

        if self.__is_flow_control_command(key_pos, token):
            return True

        if token.string in {"new", "class", "import"} or (
            token.string == "function"
            and
            len(self.command) == key_pos + 4
            and self.command[key_pos + 2].token_type == TokenType.PAREN_ROUND
            and self.command[key_pos + 3].token_type == TokenType.PAREN_CURLY
        ) or is_decorator(token.string):
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) can only be used in load function", token, self.tokenizer)
        if len(self.command[key_pos:]) >= 2 and self.command[key_pos +
                                                             1].token_type == TokenType.PAREN_ROUND:
            if len(self.command[key_pos:]) > 2:
                if token.string == "unless":
                    raise JMCSyntaxException(
                        f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True, suggestion="Did you mean `if (!...`? ('unless' is not a keyword)")
                raise JMCSyntaxException(
                    f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True)

            if self.command[key_pos + 1].string != "()":
                raise JMCSyntaxException(
                    f"Argument is not supported in custom function({token.string}).\nExpected 0 argument, `()`", self.command[key_pos], self.tokenizer, suggestion="You might have misspelled the built-in function name. (It is case-sensitive.)")
            func = convention_jmc_to_mc(token, self.tokenizer)
            self.lexer.datapack.functions_called[func] = token, self.tokenizer
            append_commands(self.__commands,
                            f"function {self.lexer.datapack.namespace}:{func}")
            return True

        if token.string not in VANILLA_COMMANDS and token.string not in Header().commands:
            if not self.command_strings:
                raise JMCSyntaxException(
                    f"Unrecognized command ({token.string})", token, self.tokenizer)

            # if not self.command_strings[-1].startswith("execute"):
            #     # for _cmd in ALLOW_KEYWORD_AFTER_CURLY_PAREN:
            #     #     if self.command_strings[-1].startswith(_cmd):
            #     #         self.command_strings[-1] += " " + token.string
            #     #         return True
            #     raise JMCSyntaxException(
            # f"Unrecognized command ({token.string})", token, self.tokenizer)

            # for _cmd in ALLOW_KEYWORD_AFTER_CURLY_PAREN:
            #     if _cmd in self.command_strings[-1]:
            #         self.command_strings[-1] += " " + token.string
            #         return True

            raise JMCSyntaxException(
                f"Unrecognized command ({token.string})", token, self.tokenizer)

        if self.__optimize(token):
            return False
        append_commands(self.__commands, token.string)
        return False

    def __is_number(self, key_pos: int, token: Token) -> None:
        if len(self.command[key_pos:]) > 1:
            raise JMCSyntaxException(
                "Unexpected token", self.command[key_pos + 1], self.tokenizer, display_col_length=False)

        if not self.command_strings:
            raise JMCSyntaxException(
                "Expected command, got number", token, self.tokenizer, display_col_length=False)

        # if not self.command_strings[-1].startswith("execute"):
        #     for _cmd in ALLOW_KEYWORD_AFTER_CURLY_PAREN:
        #         if self.command_strings[-1].startswith(_cmd):
        #             self.command_strings[-1] += " " + token.string
        #             return
        #     raise JMCSyntaxException(
        #         "Unexpected number", token, self.tokenizer, display_col_length=False)

        # for _cmd in ALLOW_KEYWORD_AFTER_CURLY_PAREN:
        #     if _cmd in self.command_strings[-1]:
        #         self.command_strings[-1] += " " + token.string
        #         return

        raise JMCSyntaxException(
            "Unexpected number", token, self.tokenizer, display_col_length=False)

    def __is_say(self, key_pos: int, token: Token) -> None:
        if len(self.command[key_pos:]) == 1:
            raise JMCSyntaxException(
                "Expected string after 'say' command", token, self.tokenizer)

        if self.command[key_pos + 1].token_type != TokenType.STRING:
            raise JMCSyntaxException(
                "Expected string after 'say' command", self.command[key_pos + 1], self.tokenizer, suggestion="(In JMC, you are required to wrapped say command's argument in quote.)")

        if len(self.command[key_pos:]) > 2:
            raise JMCSyntaxException(
                "Unexpected token", self.command[key_pos + 2], self.tokenizer, display_col_length=False)

        if "\n" in self.command[key_pos + 1].string:
            raise JMCSyntaxException(
                "Unexpected newline in say command", self.command[key_pos + 1], self.tokenizer, suggestion=r"Use '\\n' instead of '\n'")
        append_commands(
            self.__commands, f"say {self.command[key_pos+1].string}")

    def __is_schedule(self, key_pos: int) -> bool:
        if len(self.command) < key_pos + 3:
            return False
        if (
            self.command[key_pos + 2].token_type == TokenType.PAREN_CURLY
        ):
            # `schedule 1t {say "command";}`
            append_commands(self.__commands, "schedule")
            append_commands(self.__commands, self.lexer.datapack.add_arrow_function(
                "anonymous", self.command[key_pos + 2], self.tokenizer, force_create_func=True))
            append_commands(self.__commands, self.command[key_pos + 1].string)
            return True
        if len(self.command) < key_pos + 4:
            return False
        if (
            self.command[key_pos + 2].token_type == TokenType.KEYWORD
            and
            self.command[key_pos + 3].token_type == TokenType.PAREN_ROUND
        ):
            # `schedule function myFunc() 1t append;`
            if self.command[key_pos + 1].string not in {"function", "clear"}:
                raise JMCSyntaxException(
                    "Expected 'function' or 'clear' after 'schedule'", self.command[key_pos + 1], self.tokenizer)
            if self.command[key_pos + 3].string != "()":
                raise JMCSyntaxException(
                    "'schedule' does not support argument is not supported.\nExpected empty bracket", self.command[key_pos + 3], self.tokenizer)
            append_commands(self.__commands, "schedule")
            append_commands(self.__commands, self.command[key_pos + 1].string)
            append_commands(
                self.__commands,
                f"{self.lexer.datapack.namespace}:{convention_jmc_to_mc(self.command[key_pos + 2], self.tokenizer)}")
            if self.command[key_pos + 1].string == "clear":
                if len(self.command) > key_pos + 4:
                    raise JMCSyntaxException(
                        "Unexpected token in schedule clear", self.command[key_pos + 3], self.tokenizer)
                return True
            if len(self.command) < key_pos + 5:
                raise JMCSyntaxException(
                    "Expected time in schedule call", self.command[key_pos + 3], self.tokenizer)
            append_commands(self.__commands, self.command[key_pos + 4].string)
            if len(self.command) == key_pos + 6:
                if self.command[key_pos +
                                5].string not in {"append", "replace"}:
                    raise JMCSyntaxException(
                        f"Expected 'append' or 'replace' (got {self.command[key_pos + 5]}", self.command[key_pos + 5], self.tokenizer)
                append_commands(self.__commands,
                                self.command[key_pos + 5].string)
            if len(self.command) > key_pos + 6:
                raise JMCSyntaxException(
                    "Unexpected token in schedule", self.command[key_pos + 5], self.tokenizer)
            return True
        if (
            self.command[key_pos + 3].token_type == TokenType.PAREN_CURLY
        ):
            # `schedule 1t append {say "command";}`
            if self.command[key_pos +
                            2].string not in {"append", "replace"}:
                raise JMCSyntaxException(
                    f"Expected 'append' or 'replace' (got {self.command[key_pos + 2]}", self.command[key_pos + 2], self.tokenizer)
            append_commands(self.__commands, "schedule")
            append_commands(self.__commands, self.lexer.datapack.add_arrow_function(
                "anonymous", self.command[key_pos + 3], self.tokenizer, force_create_func=True))
            append_commands(self.__commands, self.command[key_pos + 1].string)
            append_commands(self.__commands, self.command[key_pos + 2].string)
            return True
        return False

    def __is_startswith_var(self, key_pos: int) -> bool:

        # I forgot what this thing do
        # if len(
        #         self.command) > key_pos + 1 and self.command[key_pos + 1].string == "run" and self.command[key_pos + 1].token_type == TokenType.KEYWORD:
        #     self.is_execute = True
        #     append_commands(self.__commands,
        #                     f"execute store result score {selector} {obj}")
        #     return False
        append_commands(self.__commands, variable_operation(
            self.command[key_pos:], self.tokenizer, self.lexer.datapack, self.is_execute, type(self), FIRST_ARGUMENTS))
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
            append_commands(self.__commands, load_once_command(
                self.command[key_pos + 1], self.lexer.datapack, self.tokenizer).call())
            return True

        execute_excluded_command = self.get_function(
            token, EXECUTE_EXCLUDED_COMMANDS)
        if execute_excluded_command is not None:
            if self.is_execute:
                append_commands(self.__commands, self.lexer.datapack.add_raw_private_function("anonymous", [execute_excluded_command(
                    self.command[key_pos + 1], self.lexer.datapack, self.tokenizer).call()]))
            else:
                append_commands(self.__commands, execute_excluded_command(
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
            append_commands(self.__commands, load_only_command(
                self.command[key_pos + 1], self.lexer.datapack, self.tokenizer).call())
            return True

        jmc_command = self.get_function(token, JMC_COMMANDS)
        if jmc_command is not None:
            if len(self.command) > key_pos + 2:
                raise JMCSyntaxException(
                    "Unexpected token", self.command[key_pos + 2], self.tokenizer, display_col_length=False, suggestion="Expected semicolon")
            append_commands(self.__commands, jmc_command(
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
                append_commands(self.__commands, return_value)
            return True
        return False

    def get_function(self, token: Token,
                     command_functions: dict[str, type["JMCFunction"]]) -> type["JMCFunction"] | None:
        """
        Get jmc function (class)

        :return: The JMCFunction's subclass
        """
        return command_functions.get(token.string, None)
