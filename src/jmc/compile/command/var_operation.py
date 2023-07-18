"""Module handling variable operation"""
from typing import TYPE_CHECKING

from .jmc_function import JMCFunction, FuncType
from ..datapack import DataPack
from ..exception import JMCSyntaxException
from ..tokenizer import Token, TokenType, Tokenizer
from .utils import find_scoreboard_player_type, PlayerType, is_obj_selector, merge_obj_selector

if TYPE_CHECKING:
    from jmc.compile.lexer_func_content import FuncContent

VAR_OPERATION_COMMANDS = JMCFunction.get_subclasses(
    FuncType.VARIABLE_OPERATION)


def variable_operation(
        tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack, is_execute: bool, FuncContent: type["FuncContent"], first_arguments: set[str]) -> str:
    """
    Parse statement for variable operation including custom JMC command that return and integer to be stored in scoreboard value

    :param tokens: Statement(List of tokens) for parsing
    :param tokenizer: Tokenizer
    :param datapack: Datapack object
    :param is_execute: Whether the statement/function is in `/execute`
    :return: Full minecraft command
    """
    if tokens[0].string.startswith(DataPack.VARIABLE_SIGN):
        objective_name = DataPack.var_name
    elif is_obj_selector(tokens):
        merged_token = merge_obj_selector(
            tokens,
            tokenizer,
            datapack)
        scoreboard_player = find_scoreboard_player_type(
            merged_token, tokenizer, allow_integer=False)
        if isinstance(scoreboard_player.value, int):
            raise ValueError("Unexpected scoreboard player type")
        objective_name, selector_string = scoreboard_player.value
        tokens[0] = Token(
            tokens[0].token_type,
            tokens[0].line,
            tokens[0].col,
            selector_string, tokens[0]._macro_length)
    else:
        raise JMCSyntaxException(
            "Invalid objective:selector[] syntax", tokens[0], tokenizer)

    if len(tokens) > 3 and tokens[2].string == "-":
        tokens[2] = tokenizer.merge_tokens(tokens[2:4])
        del tokens[3]

    if tokens[0].string.endswith(".get") and len(
            tokens) > 1 and tokens[1].token_type == TokenType.PAREN_ROUND:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                "Unexpected token", tokens[2], tokenizer)

        if tokens[1].string != "()":
            raise JMCSyntaxException(
                "'get' method takes no arguments, expected empty bracket, `.get()`", tokens[1], tokenizer)

        return f"scoreboard players get {tokens[0].string[:-4]} {objective_name}"

    if len(tokens) == 1:
        raise JMCSyntaxException(
            "Expected operator after variable", tokens[0], tokenizer, col_length=True)

    if tokens[1].token_type != TokenType.OPERATOR:
        raise JMCSyntaxException(
            f"Expected operator or 'matches' (got {tokens[1].token_type.value})", tokens[1], tokenizer)

    operator = tokens[1].string

    if operator == "=" and len(
            tokens) > 2 and tokens[2].string in first_arguments:
        func_content = FuncContent(tokenizer, [tokens[2:]],
                                   is_load=False, lexer=datapack.lexer).parse()
        if len(func_content) > 1:
            raise JMCSyntaxException(
                "Operator '=' does not support command that return multiple commands", tokens[2], tokenizer)
        if func_content[0].startswith("execute"):
            # len("execute ") = 8
            return f"execute store result score {tokens[0].string} {objective_name} {func_content[0][8:]}"
        return f"execute store result score {tokens[0].string} {objective_name} run {func_content[0]}"

    if operator == "=" and len(
            tokens) > 2 and tokens[2].token_type == TokenType.KEYWORD and tokens[2].string in {"true", "false"}:
        if len(tokens) > 3:
            raise JMCSyntaxException(
                f"Unexpected token ('{tokens[3].string}') after '{tokens[2].string}'", tokens[3], tokenizer, suggestion="Probably missing semicolon.")
        return f"scoreboard players set {tokens[0].string} {objective_name} {'1' if tokens[2].string == 'true' else '0'}"

    if operator in {"++", "--"}:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                f"Unexpected token ('{tokens[2].string}') after '{tokens[1].string}'", tokens[2], tokenizer)
        if operator == "++":
            return f"scoreboard players add {tokens[0].string} {objective_name} 1"
        if operator == "--":
            return f"scoreboard players remove {tokens[0].string} {objective_name} 1"
    elif operator == "?=":
        if len(tokens) == 2:
            raise JMCSyntaxException(
                f"Expected command after operator{tokens[1].string} (got nothing)", tokens[1], tokenizer)
        func_content = FuncContent(tokenizer, [tokens[2:]],
                                   is_load=False, lexer=datapack.lexer).parse()
        if len(func_content) > 1:
            raise JMCSyntaxException(
                "Operator '?=' does not support command that return multiple commands", tokens[2], tokenizer)
        if func_content[0].startswith("execute"):
            # len("execute ") = 8
            return f"execute store success score {tokens[0].string} {objective_name} {func_content[0][8:]}"
        return f"execute store success score {tokens[0].string} {objective_name} run {func_content[0]}"
    elif operator in {"+=", "-=", "*=", "/=", "%=", "++", "--", "><", "->", ">", "<", "=", "??="}:
        if len(tokens) == 2:
            raise JMCSyntaxException(
                f"Expected keyword after operator{tokens[1].string} (got nothing)", tokens[1], tokenizer, suggestion="Expected integer or variable or target selector")
        # if tokens[2].token_type == TokenType.OPERATOR and len(
        #         tokens) > 3 and tokens[3].token_type == TokenType.KEYWORD:
        #     tokens[2] = tokenizer.merge_tokens(tokens[2:4])
        #     del tokens[3]
        if tokens[2].token_type != TokenType.KEYWORD:
            raise JMCSyntaxException(
                f"Expected keyword after operator{tokens[1].string} (got {tokens[2].token_type.value})", tokens[2], tokenizer, suggestion="Expected integer or variable or target selector")

        if operator == "=" and tokens[2].token_type == TokenType.KEYWORD and tokens[2].string in VAR_OPERATION_COMMANDS:
            if len(tokens) == 3:
                raise JMCSyntaxException(
                    "Expected round bracket '(' after variable operation function", tokens[2], tokenizer, col_length=True)

            if tokens[3].token_type != TokenType.PAREN_ROUND:
                raise JMCSyntaxException(
                    f"Expected round bracket '(' (got {tokens[3].string})", tokens[3], tokenizer, col_length=True)

            if len(tokens) > 4:
                raise JMCSyntaxException(
                    "Unexpected token", tokens[4], tokenizer)

            return VAR_OPERATION_COMMANDS[tokens[2].string](
                tokens[3], datapack, tokenizer, var=tokens[0].string, is_execute=is_execute).call()

        left_token = tokens[0]
        right_token = tokens[2]
        # left_token.string operator right_token.string

        if len(tokens) > 3:
            if (is_obj_selector(tokens, 2)):  # If rvar is obj:selector
                right_token = merge_obj_selector(
                    tokens, tokenizer, datapack, 2)
            else:
                raise JMCSyntaxException(
                    f"Unexpected token ('{tokens[3].string}') after variable/integer ('{tokens[2].string}')", tokens[3], tokenizer, suggestion="Probably missing semicolon.")

        scoreboard_player = find_scoreboard_player_type(
            right_token, tokenizer, allow_integer=False)

        if operator == "->":
            if scoreboard_player.player_type == PlayerType.INTEGER:
                raise JMCSyntaxException(
                    "Cannot copy score into integer", right_token, tokenizer)
            if isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is int")

            return f"scoreboard players operation {scoreboard_player.value[1]} {scoreboard_player.value[0]} = {left_token.string} {objective_name}"

        if scoreboard_player.player_type == PlayerType.INTEGER:
            if operator == "+=":
                if scoreboard_player.value < 0:  # type: ignore
                    return f"scoreboard players remove {left_token.string} {objective_name} {scoreboard_player.value*-1}"
                return f"scoreboard players add {left_token.string} {objective_name} {scoreboard_player.value}"
            if operator == "-=":
                if scoreboard_player.value < 0:  # type: ignore
                    return f"scoreboard players add {left_token.string} {objective_name} {scoreboard_player.value*-1}"
                return f"scoreboard players remove {left_token.string} {objective_name} {scoreboard_player.value}"
            if operator == "=":
                return f"scoreboard players set {left_token.string} {objective_name} {scoreboard_player.value}"
            if operator == "??=":
                if scoreboard_player.value == 0:
                    return f"scoreboard players add {left_token.string} {objective_name} 0"
                else:
                    return f"execute unless score {left_token.string} {objective_name} = {left_token.string} {objective_name} run scoreboard players set {left_token.string} {objective_name} {scoreboard_player.value}"

            if not isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is not int")
            datapack.add_int(scoreboard_player.value)
            return f"scoreboard players operation {left_token.string} {objective_name} {operator} {scoreboard_player.value} {DataPack.int_name}"

        if isinstance(scoreboard_player.value, int):
            raise ValueError("scoreboard_player.value is int")

        if operator == "??=":
            return f"execute unless score {left_token.string} {objective_name} = {left_token.string} {objective_name} run scoreboard players operation {left_token.string} {objective_name} = {scoreboard_player.value[1]} {scoreboard_player.value[0]}"
        else:
            return f"scoreboard players operation {left_token.string} {objective_name} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}"

    raise JMCSyntaxException(
        f"Unrecognized operator ({operator})", tokens[1], tokenizer)
