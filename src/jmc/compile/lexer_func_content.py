"""Module responsible for handling all Function Content parsing in Lexer"""
from enum import Enum, auto
from typing import TYPE_CHECKING
from json import dumps


from .vanilla_command import COMMANDS as VANILLA_COMMANDS
from .tokenizer import Tokenizer, Token, TokenType
from .command.utils import hardcode_parse_calc, verify_args
from .exception import EXCEPTIONS, JMCSyntaxException, MinecraftSyntaxWarning
from .log import Logger
from .utils import convention_jmc_to_mc, is_decorator, is_number, is_connected, search_to_string
from .datapack import DataPack
from .command.condition import BOOL_FUNCTIONS
from .command.nbt_operation import extract_nbt, get_nbt_type, NBTType, nbt_operation
from .header import Header
from .command import (FLOW_CONTROL_COMMANDS,
                      variable_operation,
                      JMCFunction,
                      FuncType,
                      )

if TYPE_CHECKING:
    from .lexer import Lexer

logger = Logger(__name__)
SKIP_TO_NEXT_LINE = True
CONTINUE_LINE = False

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
    "give": {"effect", "recipe", "give", "loot"},
    "clear": {"effect", "schedule"},
    "if": {"execute"},
    "summon": {"execute"},
    "function": {"schedule"},
    "trigger": {"scoreboard"},
    "bossbar": {"execute"},
    "title": {"title"},
    "item": {"summon"},
    "loot": {"loot", "give"},
    "data": {"execute", "with"},
    "weather": {"playsound"},
    "item": {"particle"}
}
"""Dictionary of (FIRST_ARGUMENTS that can also be used as normal argument in a command) and (those commands)

Example: `/effect clear` -> `"clear": {"effect"}`"""


def append_commands(commands: list[str], string: str) -> None:
    """
    Append a new argument to a comand(list of minecraft arguments)

    :param commands: Entire command(list of minecraft arguments) to add to
    :param string: A new argument to add
    """
    if commands and commands[-1] == "run" and string.startswith(
            "execute ") and commands[-2] != "return":
        commands[-1] = string[8:]  # len('execute ') = 8
    else:
        commands.append(string)


class FuncContent:
    """
    A class representation of a raw function for parsing content inside the function
x
    :param tokenizer: Tokenizer
    :param programs: List of commands(List of arguments(Token))
    :param is_load: Whether the function is a load function
    """
    __slots__ = (
        "tokenizer",
        "programs",
        "is_load",
        "command_strings",
        "__commands",
        "command",
        "is_expect_command",
        "is_execute",
        "lexer",
        "expanded_commands",
        "was_anonym_func",
        "prefix")

    command: list[Token]
    is_expect_command: bool
    expanded_commands: list[str] | None
    is_execute: bool
    was_anonym_func: bool
    """Whether the last command function, this is implement for using `with` with anonymous function."""

    def __init__(self, tokenizer: Tokenizer,
                 programs: list[list[Token]], is_load: bool, lexer: "Lexer", prefix: str) -> None:

        self.tokenizer = tokenizer
        self.programs = programs
        self.is_load = is_load
        self.command_strings: list[str] = []
        self.__commands: list[str] = []
        self.lexer = lexer
        self.expanded_commands = None
        self.was_anonym_func = False
        self.prefix = prefix

    def parse_self_command(self, current_line: int):
        """
        Parse self.command
        """
        if self.command[0].token_type != TokenType.KEYWORD and get_nbt_type(
                self.command) is None:
            raise JMCSyntaxException(
                f"Expected keyword (got {self.command[0].token_type.value})", self.command[0], self.tokenizer)
        if self.command[0].string == "class":
            raise JMCSyntaxException(
                "'class' keyword found in function", self.command[0], self.tokenizer)
        # if is_decorator(self.command[0].string):
        #     raise JMCSyntaxException(
        #         "Decorated function declaration found in function", self.command[0], self.tokenizer)
        if self.command[0].string == "import":
            raise JMCSyntaxException(
                "Importing found in function", self.command[0], self.tokenizer)

        if self.command[0].string == "function" and not self.lexer._is_vanilla_func(
                self.command):
            self.lexer.parse_func(
                self.tokenizer,
                self.command,
                self.tokenizer.file_path,
                prefix=self.prefix)
            return
        elif is_decorator(self.command[0].string):
            self.lexer.parse_decorated_function(
                self.tokenizer, self.command, self.tokenizer.file_path)
            return
        elif self.command[0].string == "new":
            self.lexer.parse_new(self.tokenizer, self.command)
            return

        # Boxes check
        if self.lexer.do_while_box is not None:
            if self.command[0].string != "while":
                raise JMCSyntaxException(
                    "Expected 'while'", self.command[0], self.tokenizer)
        if self.lexer.if_else_box:
            if self.command[0].string != "else":
                append_commands(
                    self.__commands, self.lexer.parse_if_else(
                        self.tokenizer, self.prefix))

        if self.__commands:
            if self.expanded_commands is not None:
                for expanded_command in self.expanded_commands:
                    self.command_strings.append(
                        " ".join(self.__commands) + " " + (expanded_command if "\n" not in expanded_command else self.lexer.datapack.add_private_function('expand', expanded_command)))
            else:
                self.command_strings.append(" ".join(self.__commands))
            self.__commands = []
            self.expanded_commands = None

        self.__parse_commands(current_line)

    def parse(self) -> list[str]:
        """
        Parse the content
        :return: List of commands(String)
        """
        for current_line, command in enumerate(self.programs):
            self.command = command
            self.parse_self_command(current_line)

        # Boxes check
        if self.lexer.do_while_box is not None:
            raise JMCSyntaxException(
                "Expected 'while'", self.programs[-1][-1], self.tokenizer)
        if self.lexer.if_else_box:
            append_commands(
                self.__commands,
                self.lexer.parse_if_else(
                    self.tokenizer, self.prefix))

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

    def __parse_commands(self, current_line: int) -> None:
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
            if self.__expect_command(key_pos, token, current_line):
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
            and self.__commands[-2] != "return"
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
            if not self.is_execute and self.__commands[-1] != "return":
                raise MinecraftSyntaxWarning(
                    "'run' keyword found outside 'execute' command", token, self.tokenizer)
            self.is_expect_command = True

        if token.string == "expand" and token.token_type == TokenType.KEYWORD:
            if self.is_execute:
                self.is_expect_command = True
                self.expanded_commands = []

        __token_string = token.string
        if __token_string.startswith("$"):
            __token_string = __token_string[1:]
        __is_first_arg = (
            __token_string in FIRST_ARGUMENTS
            or
            __token_string in Header().commands
            or is_decorator(__token_string)
        )
        __is_not_exception = (
            len(self.__commands) > command_pos and
            not (
                __token_string in FIRST_ARGUMENTS_EXCEPTION
                and
                self.command[command_pos].string in FIRST_ARGUMENTS_EXCEPTION[__token_string]
            )
        )
        __is_not_connected = not is_connected(token, self.command[key_pos - 1])
        __is_not_deleted = __token_string not in Header().dels

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

    def __expect_command(self, key_pos: int, token: Token,
                         current_line: int) -> bool:
        """
        Called when expecting a command

        :param key_pos: Current index in self.command
        :param token: token
        :return: Whether to break out of the loop
        """
        self.is_expect_command = False
        if token.string == "execute":
            self.is_execute = True

        __nbt_type = get_nbt_type(self.command[key_pos:])

        # Handle Errors
        if token.token_type != TokenType.KEYWORD and __nbt_type is None:
            if not (token.token_type ==
                    TokenType.PAREN_CURLY and (self.is_execute or self.__commands[key_pos - 2] == "return")):
                raise JMCSyntaxException(
                    "Expected keyword", token, self.tokenizer)
            if self.expanded_commands is not None:
                self.expanded_commands = self.lexer.datapack.parse_function_token(
                    token, self.tokenizer, self.prefix)
                self.__commands[-1] = "run"
                return SKIP_TO_NEXT_LINE
            force_create_func = (
                len(self.programs) > current_line + 1 and
                self.programs[current_line + 1][0].string == "with"
            )
            append_commands(self.__commands, self.lexer.datapack.add_arrow_function(
                "anonymous", token, self.tokenizer, self.prefix, force_create_func=force_create_func))
            self.was_anonym_func = True
            return SKIP_TO_NEXT_LINE
        # End Handle Errors

        if token.string == "with":
            self.__handle_with(key_pos, token)
            __with_nbt_type = get_nbt_type(self.command[key_pos + 1:])
            if __with_nbt_type is None:
                return CONTINUE_LINE
            nbt_type_str, target, path = extract_nbt(
                self.command, self.tokenizer, self.lexer.datapack, __with_nbt_type, start_index=key_pos + 1)
            append_commands(
                self.__commands,
                f"{nbt_type_str} {target}{path}")
            return SKIP_TO_NEXT_LINE
        self.was_anonym_func = False

        if is_number(token.string) and key_pos == 0:
            self.__handle_number(key_pos, token)
            return SKIP_TO_NEXT_LINE

        if token.string == "say":
            self.__handle_say(key_pos, token)
            return SKIP_TO_NEXT_LINE

        if token.string == "function" and len(
                self.command) == key_pos + 2 and self.command[key_pos + 1].token_type == TokenType.STRING:
            append_commands(self.__commands,
                            f"function {self.command[key_pos + 1].string}")
            return SKIP_TO_NEXT_LINE

        if token.string == "schedule":
            if self.__handle_schedule(key_pos):
                return SKIP_TO_NEXT_LINE

        if token.string == "$" and len(
                self.command) > key_pos + 1 and self.command[key_pos + 1].token_type == TokenType.PAREN_ROUND:
            append_commands(self.__commands, token.string)
            return CONTINUE_LINE

        if token.string == "return":
            self.__handle_return(key_pos)
            return CONTINUE_LINE

        if token.string.startswith(DataPack.VARIABLE_SIGN):
            if self.__handle_startswith_var(key_pos):
                return SKIP_TO_NEXT_LINE

        if __nbt_type is not None:
            self.__handle_startswith_nbt(key_pos, __nbt_type)
            return SKIP_TO_NEXT_LINE

        if len(self.command[key_pos:]
               ) > 2 and self.command[key_pos + 1].string == ":":
            if self.__handle_startswith_var(key_pos):
                return SKIP_TO_NEXT_LINE

        if self.__is_jmc_function(key_pos, token):
            if len(self.command[key_pos:]) > 2:
                raise JMCSyntaxException(
                    f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True)
            return SKIP_TO_NEXT_LINE

        if self.__is_flow_control_command(key_pos, token):
            return SKIP_TO_NEXT_LINE

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
            return self.__handle_function_call(key_pos, token)

        if token.string not in VANILLA_COMMANDS and token.string not in Header(
        ).commands:
            if not self.command_strings:
                raise JMCSyntaxException(
                    f"Unrecognized command ({token.string})", token, self.tokenizer)
            raise JMCSyntaxException(
                f"Unrecognized command ({token.string})", token, self.tokenizer)

        if self.__optimize(token):
            return CONTINUE_LINE
        append_commands(self.__commands, token.string)
        return CONTINUE_LINE

    def __handle_function_call(self, key_pos: int, token: Token) -> bool:
        if len(self.command[key_pos:]) > 2:  # func_name() with ...
            if token.string == "unless":
                raise JMCSyntaxException(
                    f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True, suggestion="Did you mean `if (!...`? ('unless' is not a keyword)")

            if self.command[key_pos + 2].string != "with":
                raise JMCSyntaxException(
                    f"Unexpected token({self.command[key_pos+2].string}) after function call. Expected semicolon(;)", self.command[key_pos + 1], self.tokenizer, col_length=True)

            if self.command[key_pos + 1].string != "()":
                raise JMCSyntaxException(
                    f"Argument is not supported in custom function({token.string}) with `with` syntax.\nExpected 0 argument, `()`", self.command[key_pos], self.tokenizer, suggestion="You might have misspelled the built-in function name. (It is case-sensitive.)")
            func = convention_jmc_to_mc(token, self.tokenizer, self.prefix)
            self.lexer.datapack.functions_called[func] = token, self.tokenizer
            append_commands(self.__commands,
                            f"function {self.lexer.datapack.format_func_path(func)}")
            del self.command[key_pos + 1]  # delete ()

            __with_nbt_type = get_nbt_type(self.command[key_pos + 2:])
            if __with_nbt_type is None:
                return CONTINUE_LINE

            append_commands(self.__commands, "with")
            nbt_type_str, target, path = extract_nbt(
                self.command, self.tokenizer, self.lexer.datapack, __with_nbt_type, start_index=key_pos + 2)
            append_commands(
                self.__commands,
                f"{nbt_type_str} {target}{path}")
            return SKIP_TO_NEXT_LINE

        if self.command[key_pos + 1].string != "()":
            arg_token = self.command[key_pos + 1]
            func = convention_jmc_to_mc(token, self.tokenizer, self.prefix)
            args, kwargs = self.tokenizer.parse_func_args(arg_token)
            if func in self.lexer.datapack.lazy_func:
                __command = self.lexer.datapack.lazy_func[func].handle_lazy(
                    args, kwargs, self.command[key_pos + 1], hardcode_parse_calc)
                if self.is_execute and "\n" in __command:
                    raise JMCSyntaxException(
                        "Lazy function with multiple commands cannot be used with execute.",
                        self.command[key_pos],
                        self.tokenizer)
                append_commands(self.__commands,
                                __command)
                return SKIP_TO_NEXT_LINE

            self.lexer.datapack.functions_called[func] = token, self.tokenizer
            if args:
                if len(args) > 1:
                    raise JMCSyntaxException(
                        f"Expected 1 position argument (got {len(args)})", arg_token, self.tokenizer, suggestion='The positional argument syntax is `func({"key":"value"});`. You might be going for `func(key="value")` syntax. If this is intended to be a lazy function, it has to be defined BEFORE using.')
                if kwargs:
                    raise JMCSyntaxException(
                        f"Expected exclusively positional or keyword argument", arg_token, self.tokenizer, suggestion='The positional argument syntax is `func({"key":"value"});`. You might be going for `func(key="value")` syntax')
                if len(args[0]) > 1:
                    raise JMCSyntaxException(
                        f"Unexpected token after `{{}}` in positional argument syntax", arg_token, self.tokenizer, suggestion='The positional argument syntax is `func({"key":"value"});`. You might be going for `func(key="value")` syntax')
                if args[0][0].token_type != TokenType.PAREN_CURLY:
                    raise JMCSyntaxException(
                        f"Expected curly parenthesis({{}}) (got {args[0][0].token_type.value}) in positional argument syntax",
                        arg_token,
                        self.tokenizer,
                        suggestion='The positional argument syntax is `func({"key":"value"});`. You might be going for `func(key="value")` syntax. If this is meant to be a built-in function call, you may have misspelled it')
                append_commands(self.__commands,
                                f"function {self.lexer.datapack.format_func_path(func)} {self.lexer.clean_up_paren_token(args[0][0], self.tokenizer)}")
                return SKIP_TO_NEXT_LINE
            if kwargs:
                json = {}
                for key, value in kwargs.items():
                    if len(value) > 1:
                        raise JMCSyntaxException(
                            f"Expected 1 string token after `=` (got {len(value)}) in keyword argument syntax", arg_token, self.tokenizer, suggestion='The keyword argument syntax is `func(key="value")`')
                    if value[0].token_type != TokenType.STRING:
                        raise JMCSyntaxException(
                            f"Expected string as key in keyword argument syntax (got {value[0].token_type.value})", arg_token, self.tokenizer, suggestion='The keyword argument syntax is `func(key="value")`')
                    json[key] = value[0].string
                append_commands(self.__commands,
                                f"function {self.lexer.datapack.format_func_path(func)} {dumps(json, separators=(',', ':'))}")
                return SKIP_TO_NEXT_LINE

            raise JMCSyntaxException(
                f"Unrecognized vanilla macro syntax", arg_token, self.tokenizer, suggestion='Available syntaxes are `func({"key":"value"});`, `func(key="value")`')

        func = convention_jmc_to_mc(token, self.tokenizer, self.prefix)
        if func in self.lexer.datapack.lazy_func:
            __command = self.lexer.datapack.lazy_func[func].handle_lazy(
                [], {}, self.command[key_pos + 1], hardcode_parse_calc)
            if self.is_execute and "\n" in __command:
                raise JMCSyntaxException(
                    "Lazy function with multiple commands cannot be used with execute.",
                    self.command[key_pos],
                    self.tokenizer)
            append_commands(self.__commands,
                            __command)
            return SKIP_TO_NEXT_LINE
        self.lexer.datapack.functions_called[func] = token, self.tokenizer
        append_commands(self.__commands,
                        f"function {self.lexer.datapack.format_func_path(func)}")
        return SKIP_TO_NEXT_LINE

    def __handle_number(self, key_pos: int, token: Token) -> None:
        if len(self.command[key_pos:]) > 1:
            raise JMCSyntaxException(
                "Unexpected token", self.command[key_pos + 1], self.tokenizer, display_col_length=False)

        if not self.command_strings:
            raise JMCSyntaxException(
                "Expected command, got number", token, self.tokenizer, display_col_length=False)

        raise JMCSyntaxException(
            "Unexpected number", token, self.tokenizer, display_col_length=False)

    def __handle_return(self, key_pos: int) -> None:
        if self.command[key_pos + 1].string == "true":
            append_commands(self.__commands, "return 1")
            del self.command[key_pos + 1]
        elif self.command[key_pos + 1].string == "false":
            append_commands(self.__commands, "return 0")
            del self.command[key_pos + 1]
        else:
            append_commands(self.__commands, "return")

    def __handle_with(self, key_pos: int, token: Token) -> None:
        if not self.was_anonym_func:
            first_section, second_section = self.command_strings.pop().split(" run ")
            append_commands(
                self.__commands,
                f"{first_section} run {self.lexer.datapack.add_private_function('anonymous', second_section, force_create_func=True)}")
            if self.command[key_pos + 1].token_type != TokenType.PAREN_CURLY:
                append_commands(self.__commands, "with")
            return
        self.lexer.datapack.version.require(16, token, self.tokenizer)
        append_commands(self.__commands, self.command_strings.pop())
        if self.command[key_pos + 1].token_type != TokenType.PAREN_CURLY:
            append_commands(self.__commands, "with")

    def __handle_say(self, key_pos: int, token: Token) -> None:
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

    def __handle_schedule(self, key_pos: int) -> bool:
        if len(self.command) < key_pos + 3:
            return CONTINUE_LINE
        if (
            self.command[key_pos + 2].token_type == TokenType.PAREN_CURLY
        ):
            # `schedule 1t {say "command";}`
            append_commands(self.__commands, "schedule")
            append_commands(self.__commands, self.lexer.datapack.add_arrow_function(
                "anonymous", self.command[key_pos + 2], self.tokenizer, self.prefix, force_create_func=True))
            append_commands(self.__commands, self.command[key_pos + 1].string)
            return SKIP_TO_NEXT_LINE
        if len(self.command) < key_pos + 4:
            return CONTINUE_LINE
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
                f"{self.lexer.datapack.namespace}:{convention_jmc_to_mc(self.command[key_pos + 2], self.tokenizer, self.prefix)}")
            if self.command[key_pos + 1].string == "clear":
                if len(self.command) > key_pos + 4:
                    raise JMCSyntaxException(
                        "Unexpected token in schedule clear", self.command[key_pos + 3], self.tokenizer)
                return SKIP_TO_NEXT_LINE
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
            return SKIP_TO_NEXT_LINE
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
                "anonymous", self.command[key_pos + 3], self.tokenizer, self.prefix, force_create_func=True))
            append_commands(self.__commands, self.command[key_pos + 1].string)
            append_commands(self.__commands, self.command[key_pos + 2].string)
            return SKIP_TO_NEXT_LINE
        return CONTINUE_LINE

    def __handle_startswith_nbt(self, key_pos: int, nbt_type: NBTType):
        append_commands(self.__commands, nbt_operation(
            self.command[key_pos:], self.tokenizer, self.lexer.datapack, nbt_type, FuncContent, self.prefix))

    def __handle_startswith_var(self, key_pos: int) -> bool:
        if self.command[0].string == "$if":
            # special case
            return CONTINUE_LINE
        try:
            append_commands(self.__commands, variable_operation(
                self.command[key_pos:], self.tokenizer, self.lexer.datapack, self.is_execute, type(self), FIRST_ARGUMENTS, self.prefix))
        except EXCEPTIONS as var_error:
            if key_pos != 0:
                raise var_error
            first_token = self.command[0]
            if first_token.string[0] != "$":
                raise var_error
            self.command[0] = Token(first_token.token_type,
                                    first_token.line,
                                    first_token.col + 1,
                                    first_token.string[1:],
                                    first_token._macro_length)
            if not self.command[0].string:
                del self.command[0]
            if len(self.command) == 0:
                raise JMCSyntaxException(
                    "Unexpected variable without name (`$`)", first_token, self.tokenizer)
            try:
                self.parse_self_command(0)
            except EXCEPTIONS as normal_error:
                token = self.command[0]
                if token.string not in VANILLA_COMMANDS and token.string not in Header(
                ).commands and token.string != "":
                    raise var_error
                raise normal_error
            self.__commands[0] = "$" + self.__commands[0]
        return SKIP_TO_NEXT_LINE

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
                self.command[key_pos + 1], self.command[key_pos], self.lexer.datapack, self.tokenizer, self.prefix).call())
            return SKIP_TO_NEXT_LINE

        execute_excluded_command = self.get_function(
            token, EXECUTE_EXCLUDED_COMMANDS)
        if execute_excluded_command is not None:
            if self.is_execute:
                append_commands(self.__commands, self.lexer.datapack.add_raw_private_function("anonymous", [execute_excluded_command(
                    self.command[key_pos + 1], self.command[key_pos], self.lexer.datapack, self.tokenizer, self.prefix).call()]))
            else:
                append_commands(self.__commands, execute_excluded_command(
                    self.command[key_pos + 1], self.command[key_pos], self.lexer.datapack, self.tokenizer, self.prefix).call())
            return SKIP_TO_NEXT_LINE

        load_only_command = self.get_function(token, LOAD_ONLY_COMMANDS)
        if load_only_command is not None:
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) cannot be used with 'execute'", token, self.tokenizer)
            if not self.is_load:
                raise JMCSyntaxException(
                    f"This feature({token.string}) can only be used in load function", token, self.tokenizer)
            append_commands(self.__commands, load_only_command(
                self.command[key_pos + 1], self.command[key_pos], self.lexer.datapack, self.tokenizer, self.prefix).call())
            return SKIP_TO_NEXT_LINE

        jmc_command = self.get_function(token, JMC_COMMANDS)
        if jmc_command is not None:
            if len(self.command) > key_pos + 2:
                raise JMCSyntaxException(
                    "Unexpected token", self.command[key_pos + 2], self.tokenizer, display_col_length=False, suggestion="Expected semicolon")
            append_commands(self.__commands, jmc_command(
                self.command[key_pos + 1], self.command[key_pos], self.lexer.datapack, self.tokenizer, self.prefix, is_execute=self.is_execute).call())
            return SKIP_TO_NEXT_LINE

        if token.string in BOOL_FUNCTIONS:
            raise JMCSyntaxException(
                f"This feature({token.string}) only works in JMC's custom condition", token, self.tokenizer)

        return CONTINUE_LINE

    def __is_flow_control_command(self, key_pos: int, token: Token) -> bool:
        flow_control_command = FLOW_CONTROL_COMMANDS.get(
            token.string, None)
        if flow_control_command is not None:
            if self.is_execute:
                raise JMCSyntaxException(
                    f"This feature({token.string}) cannot be used with 'execute'", token, self.tokenizer)
            return_value = flow_control_command(
                self.command[key_pos:], self.lexer.datapack, self.tokenizer, self.prefix)
            if return_value is not None:
                append_commands(self.__commands, return_value)
            return True
        return CONTINUE_LINE

    def get_function(self, token: Token,
                     command_functions: dict[str, type["JMCFunction"]]) -> type["JMCFunction"] | None:
        """
        Get jmc function (class)

        :return: The JMCFunction's subclass
        """
        return command_functions.get(token.string, None)
