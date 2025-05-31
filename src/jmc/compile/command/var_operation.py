"""Module handling variable operation"""

from typing import TYPE_CHECKING

from jmc.compile.expression_eval import Variable, expression_to_tree, tokens_to_tokens, tree_to_operations

from ..command.builtin_function.load_only import DebugWatch
from .jmc_function import JMCFunction, FuncType
from ..datapack import DataPack
from ..exception import JMCSyntaxException, relative_file_name
from ..tokenizer import Token, TokenType, Tokenizer
from .utils import (
    find_scoreboard_player_type,
    PlayerType,
    is_obj_selector,
    merge_obj_selector,
)

if TYPE_CHECKING:
    from ..lexer_func_content import FuncContent

VAR_OPERATION_COMMANDS = JMCFunction.get_subclasses(
    FuncType.VARIABLE_OPERATION)


def variable_operation(
    tokens: list[Token],
    tokenizer: Tokenizer,
    datapack: DataPack,
    is_execute: bool,
    FuncContent: type["FuncContent"],
    first_arguments: set[str],
    prefix: str,
) -> str:
    """
    Parse statement for variable operation including custom JMC command that return and integer to be stored in scoreboard value

    :param tokens: Statement(List of tokens) for parsing
    :param tokenizer: Tokenizer
    :param datapack: Datapack object
    :param is_execute: Whether the statement/function is in `/execute`
    :param FuncContent: Dependency injection of FuncConent class
    :param first_arguments: Set of all vanilla commands and JMC custom syntax
    :return: Full minecraft command
    """
    datapack.data.is_too_late_debug_watch = True
    datapack.data.last_code_data = (relative_file_name(
        tokenizer.file_path, tokens[0].line), tokenizer.file_string.split("\n")[tokens[0].line - 1])
    is_token_obj_selector = False
    if tokens[0].string.startswith(DataPack.VARIABLE_SIGN):
        if len(tokens[0].string) == 1:
            raise JMCSyntaxException(
                "Unexpected variable without name (`$`)", tokens[0], tokenizer
            )
        if tokens[0].string[1] == DataPack.VARIABLE_SIGN:
            raise JMCSyntaxException(
                "Unexpected double variable sign", tokens[0], tokenizer
            )
        objective_name = DataPack.var_name
    elif is_obj_selector(tokens):
        is_token_obj_selector = True
        merged_token = merge_obj_selector(tokens, tokenizer, datapack)
        scoreboard_player = find_scoreboard_player_type(
            merged_token, tokenizer, allow_integer=False
        )
        if isinstance(scoreboard_player.value, int):
            raise ValueError("Unexpected scoreboard player type")
        objective_name, selector_string = scoreboard_player.value
        tokens[0] = Token(
            tokens[0].token_type,
            tokens[0].line,
            tokens[0].col,
            selector_string,
            tokens[0]._macro_length,
        )
    else:
        raise JMCSyntaxException(
            "Invalid objective:selector[] syntax", tokens[0], tokenizer
        )

    if len(tokens) > 3 and tokens[2].string == "-" and tokens[1].string != ":=":
        tokens[2] = tokenizer.merge_tokens(tokens[2:4])
        del tokens[3]

    if (
        (len(tokens) == 2 and tokens[0].string.endswith(".get"))
        or (
            len(tokens) == 3
            and tokens[1].string.endswith(".get")
            and is_token_obj_selector
        )
    ) and tokens[-1].token_type == TokenType.PAREN_ROUND:
        if tokens[-1].string != "()":
            raise JMCSyntaxException(
                "'get' method takes no arguments, expected empty bracket, `.get()`",
                tokens[1],
                tokenizer,
            )

        return f"scoreboard players get {tokens[0].string[:-4] if tokens[0].string.endswith('.get') else tokens[0].string} {objective_name}"

    if len(tokens) == 1:
        return f"scoreboard players get {tokens[0].string} {objective_name}"
        # raise JMCSyntaxException(
        #     "Expected operator after variable", tokens[0], tokenizer, col_length=True)

    if tokens[1].token_type != TokenType.OPERATOR:
        raise JMCSyntaxException(
            f"Expected operator or 'matches' (got {tokens[1].token_type.value})",
            tokens[1],
            tokenizer,
        )

    operator = tokens[1].string

    if operator == "=" and len(tokens) > 2 and tokens[2].string in first_arguments:
        func_content = FuncContent(
            tokenizer, [tokens[2:]], is_load=False, lexer=datapack.lexer, prefix=prefix
        ).parse()
        if len(func_content) > 1:
            raise JMCSyntaxException(
                "Operator '=' does not support command that return multiple commands",
                tokens[2],
                tokenizer,
            )
        if func_content[0].startswith("execute"):
            # len("execute ") = 8
            return DebugWatch.variable_operation_wrapper(f"execute store result score {tokens[0].string} {objective_name} {func_content[0][8:]}", tokens[0].string, objective_name, datapack)
        return DebugWatch.variable_operation_wrapper(f"execute store result score {tokens[0].string} {objective_name} run {func_content[0]}", tokens[0].string, objective_name, datapack)

    if (
        operator == "="
        and len(tokens) > 2
        and tokens[2].token_type == TokenType.KEYWORD
        and tokens[2].string in {"true", "false"}
    ):
        if len(tokens) > 3:
            raise JMCSyntaxException(
                f"Unexpected token ('{tokens[3].string}') after '{tokens[2].string}'",
                tokens[3],
                tokenizer,
                suggestion="Probably missing semicolon.",
            )
        return DebugWatch.variable_operation_wrapper(f"scoreboard players set {tokens[0].string} {objective_name} {'1' if tokens[2].string == 'true' else '0'}", tokens[0].string, objective_name, datapack)

    if (
        operator == "??="
        and len(tokens) > 2
        and tokens[2].token_type == TokenType.KEYWORD
        and tokens[2].string in {"true", "false"}
    ):
        if len(tokens) > 3:
            raise JMCSyntaxException(
                f"Unexpected token ('{tokens[3].string}') after '{tokens[2].string}'",
                tokens[3],
                tokenizer,
                suggestion="Probably missing semicolon.",
            )
        if tokens[2].string == "true":
            return DebugWatch.variable_operation_wrapper(f"execute unless score {tokens[0].string} {objective_name} = {tokens[0].string} {objective_name} run scoreboard players set {tokens[0].string} {objective_name} 1", tokens[0].string, objective_name, datapack)
        elif tokens[2].string == "false":
            return DebugWatch.variable_operation_wrapper(f"scoreboard players add {tokens[0].string} {objective_name} 0", tokens[0].string, objective_name, datapack)

    if operator == ":=":
        if len(tokens) == 2:
            raise JMCSyntaxException(
                f"Expected keyword after operator{tokens[1].string} (got nothing)",
                tokens[1],
                tokenizer,
                suggestion="Expected integer or variable or target selector",
            )
        expression_tokens = tokens_to_tokens(tokens[2:], tokenizer)
        expression_tree = expression_to_tree(expression_tokens, tokenizer)
        operations = tree_to_operations(expression_tree, Variable(
            f"{tokens[0].string} {objective_name}", tokens[0]))
        expression_commands: list[str] = []
        for variable_, operator_, number_ in operations:
            if " " in number_.content:  # right hand is not a constant number
                expression_commands.append(
                    f"scoreboard players operation {variable_.content} {operator_.content}= {number_.content}")
                continue
            number = int(number_.content)
            if operator_.content == "+":
                if number >= 0:
                    expression_commands.append(
                        f"scoreboard players add {variable_.content} {number}")
                else:
                    expression_commands.append(
                        f"scoreboard players remove {variable_.content} {-number}")
            elif operator_.content == "-":
                if number >= 0:
                    expression_commands.append(
                        f"scoreboard players remove {variable_.content} {number}")
                else:
                    expression_commands.append(
                        f"scoreboard players add {variable_.content} {-number}")
            elif operator_.content == "":
                expression_commands.append(
                    f"scoreboard players set {variable_.content} = {number}")
            elif operator_.content in "*/%":
                datapack.add_int(number)
                expression_commands.append(
                    f"scoreboard players operation {variable_.content} {operator_.content}= {number} {datapack.int_name}")
            else:
                raise Exception(
                    "Somehow, there's an operator JMC doesn't know")
        return DebugWatch.variable_operation_wrapper("\n".join(expression_commands), tokens[0].string, objective_name, datapack)

    if operator in {"++", "--"}:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                f"Unexpected token ('{tokens[2].string}') after '{tokens[1].string}'",
                tokens[2],
                tokenizer,
            )
        if operator == "++":
            return DebugWatch.variable_operation_wrapper(f"scoreboard players add {tokens[0].string} {objective_name} 1", tokens[0].string, objective_name, datapack)
        if operator == "--":
            return DebugWatch.variable_operation_wrapper(f"scoreboard players remove {tokens[0].string} {objective_name} 1", tokens[0].string, objective_name, datapack)
    elif operator == "?=":
        if len(tokens) == 2:
            raise JMCSyntaxException(
                f"Expected command after operator{tokens[1].string} (got nothing)",
                tokens[1],
                tokenizer,
            )
        func_content = FuncContent(
            tokenizer, [tokens[2:]], is_load=False, lexer=datapack.lexer, prefix=prefix
        ).parse()
        if len(func_content) > 1:
            raise JMCSyntaxException(
                "Operator '?=' does not support command that return multiple commands",
                tokens[2],
                tokenizer,
            )
        if func_content[0].startswith("execute"):
            # len("execute ") = 8
            return DebugWatch.variable_operation_wrapper(f"execute store success score {tokens[0].string} {objective_name} {func_content[0][8:]}", tokens[0].string, objective_name, datapack)
        return DebugWatch.variable_operation_wrapper(f"execute store success score {tokens[0].string} {objective_name} run {func_content[0]}", tokens[0].string, objective_name, datapack)
    elif operator in {
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "++",
        "--",
        "><",
        "->",
        ">",
        "<",
        "=",
        "??=",
    }:
        if len(tokens) == 2:
            raise JMCSyntaxException(
                f"Expected keyword after operator{tokens[1].string} (got nothing)",
                tokens[1],
                tokenizer,
                suggestion="Expected integer or variable or target selector",
            )

        if tokens[2].token_type not in (
            TokenType.KEYWORD,
            TokenType.OPERATOR,
            TokenType.PAREN_SQUARE,
        ):
            raise JMCSyntaxException(
                f"Expected keyword after operator{tokens[1].string} (got {tokens[2].token_type.value})",
                tokens[2],
                tokenizer,
                suggestion="Expected integer or variable or target selector",
            )

        if (
            operator == "="
            and tokens[2].token_type == TokenType.KEYWORD
            and tokens[2].string in VAR_OPERATION_COMMANDS
        ):
            if len(tokens) == 3:
                raise JMCSyntaxException(
                    "Expected round bracket '(' after variable operation function",
                    tokens[2],
                    tokenizer,
                    col_length=True,
                )

            if tokens[3].token_type != TokenType.PAREN_ROUND:
                raise JMCSyntaxException(
                    f"Expected round bracket '(' (got {tokens[3].string})",
                    tokens[3],
                    tokenizer,
                    col_length=True,
                )

            if len(tokens) > 4:
                raise JMCSyntaxException(
                    "Unexpected token", tokens[4], tokenizer)

            return VAR_OPERATION_COMMANDS[tokens[2].string](
                tokens[3],
                tokens[2],
                datapack,
                tokenizer,
                prefix,
                var=tokens[0].string + " " + objective_name,
                is_execute=is_execute,
            ).call()

        if (
            len(tokens) >= 4
            and operator == "="
            and tokens[2].token_type == TokenType.KEYWORD
            and tokens[3].token_type == TokenType.PAREN_ROUND
        ):
            func = FuncContent(
                tokenizer,
                [tokens[2:]],
                is_load=False,
                lexer=datapack.lexer,
                prefix=prefix,
            ).parse()
            if len(func) > 1:
                raise JMCSyntaxException(
                    f"Multiple commands (got {len(func)}) cannot be assigned to a variable",
                    tokens[2],
                    tokenizer,
                )
            return DebugWatch.variable_operation_wrapper(f"""execute store result score {
                tokens[0].string} {objective_name} run {func[0]}""", tokens[0].string, objective_name, datapack)

        left_token = tokens[0]
        right_token = tokens[2]
        # left_token.string operator right_token.string

        old_tokens = None
        if len(tokens) > 3 and is_obj_selector(tokens, 2):  # If rvar is obj:selector
            old_tokens = tokens.copy()
            right_token = merge_obj_selector(tokens, tokenizer, datapack, 2)

        if len(tokens) > 3:
            if operator == "=":
                try:
                    return DebugWatch.variable_operation_wrapper(f"""execute store result score {left_token.string} {objective_name} run {variable_operation(old_tokens[2:] if old_tokens is not None else tokens[2:], tokenizer, datapack, is_execute, FuncContent, first_arguments, prefix)}""".replace(
                        "run execute store", "store"
                    ), left_token.string, objective_name, datapack)
                except Exception as error:
                    try:
                        func_content = FuncContent(
                            tokenizer,
                            [old_tokens[2:] if old_tokens is not None else tokens[2:]],
                            is_load=False,
                            lexer=datapack.lexer,
                            prefix=prefix,
                        ).parse()
                        if len(func_content) > 1:
                            raise JMCSyntaxException(
                                "Operator '=' does not support command that return multiple commands",
                                tokens[2],
                                tokenizer,
                            )
                        if func_content[0].startswith("execute"):
                            # len("execute ") = 8
                            return DebugWatch.variable_operation_wrapper(f"execute store result score {tokens[0].string} {objective_name} {func_content[0][8:]}", tokens[0].string, objective_name, datapack)
                        return DebugWatch.variable_operation_wrapper(f"execute store result score {tokens[0].string} {objective_name} run {func_content[0]}", tokens[0].string, objective_name, datapack)
                    except Exception:
                        raise error
            elif operator == "??=":
                func_content = FuncContent(
                    tokenizer,
                    [old_tokens[2:] if old_tokens is not None else tokens[2:]],
                    is_load=False,
                    lexer=datapack.lexer,
                    prefix=prefix,
                ).parse()
                if len(func_content) > 1:
                    raise JMCSyntaxException(
                        "Operator '=' does not support command that return multiple commands",
                        tokens[2],
                        tokenizer,
                    )
                if func_content[0].startswith("execute"):
                    # len("execute ") = 8
                    return DebugWatch.variable_operation_wrapper(f"execute unless score {tokens[0].string} {objective_name} = {tokens[0].string} {objective_name} store result score {tokens[0].string} {objective_name} {func_content[0][8:]}", tokens[0].string, objective_name, datapack)
                return DebugWatch.variable_operation_wrapper(f"execute unless score {tokens[0].string} {objective_name} = {tokens[0].string} {objective_name} store result score {tokens[0].string} {objective_name} run {func_content[0]}", tokens[0].string, objective_name, datapack)

            else:
                raise JMCSyntaxException(
                    f"Unexpected token ('{tokens[3].string}') after variable/integer ('{tokens[2].string}')",
                    tokens[3],
                    tokenizer,
                    suggestion="Probably missing semicolon.",
                )

        scoreboard_player = find_scoreboard_player_type(
            right_token, tokenizer, allow_integer=False
        )

        if operator == "->":
            if scoreboard_player.player_type == PlayerType.INTEGER:
                raise JMCSyntaxException(
                    "Cannot copy score into integer", right_token, tokenizer
                )
            if isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is int")

            return DebugWatch.variable_operation_wrapper(f"scoreboard players operation {scoreboard_player.value[1]} {scoreboard_player.value[0]} = {left_token.string} {objective_name}", scoreboard_player.value[1], scoreboard_player.value[0], datapack)

        if scoreboard_player.player_type == PlayerType.INTEGER:
            if operator == "+=":
                if scoreboard_player.value < 0:  # type: ignore
                    return DebugWatch.variable_operation_wrapper(f"scoreboard players remove {left_token.string} {objective_name} {scoreboard_player.value * -1}", left_token.string, objective_name, datapack)
                return DebugWatch.variable_operation_wrapper(f"scoreboard players add {left_token.string} {objective_name} {scoreboard_player.value}", left_token.string, objective_name, datapack)
            if operator == "-=":
                if scoreboard_player.value < 0:  # type: ignore
                    return DebugWatch.variable_operation_wrapper(f"scoreboard players add {left_token.string} {objective_name} {scoreboard_player.value * -1}", left_token.string, objective_name, datapack)
                return DebugWatch.variable_operation_wrapper(f"scoreboard players remove {left_token.string} {objective_name} {scoreboard_player.value}", left_token.string, objective_name, datapack)
            if operator == "=":
                return DebugWatch.variable_operation_wrapper(f"scoreboard players set {left_token.string} {objective_name} {scoreboard_player.value}", left_token.string, objective_name, datapack)
            if operator == "??=":
                if scoreboard_player.value == 0:
                    return (
                        f"scoreboard players add {left_token.string} {objective_name} 0"
                    )
                else:
                    return DebugWatch.variable_operation_wrapper(f"execute unless score {left_token.string} {objective_name} = {left_token.string} {objective_name} run scoreboard players set {left_token.string} {objective_name} {scoreboard_player.value}", left_token.string, objective_name, datapack)

            if not isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is not int")
            datapack.add_int(scoreboard_player.value)
            return DebugWatch.variable_operation_wrapper(f"scoreboard players operation {left_token.string} {objective_name} {operator} {scoreboard_player.value} {DataPack.int_name}", left_token.string, objective_name, datapack)

        if isinstance(scoreboard_player.value, int):
            raise ValueError("scoreboard_player.value is int")

        if operator == "??=":
            return DebugWatch.variable_operation_wrapper(f"execute unless score {left_token.string} {objective_name} = {left_token.string} {objective_name} run scoreboard players operation {left_token.string} {objective_name} = {scoreboard_player.value[1]} {scoreboard_player.value[0]}", left_token.string, objective_name, datapack)
        else:
            return DebugWatch.variable_operation_wrapper(f"scoreboard players operation {left_token.string} {objective_name} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}", left_token.string, objective_name, datapack)

    raise JMCSyntaxException(
        f"Unrecognized operator ({operator})", tokens[1], tokenizer
    )
