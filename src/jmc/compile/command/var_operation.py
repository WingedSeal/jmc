"""Module handling variable operation"""
from .jmc_function import JMCFunction, FuncType
from ..datapack import DataPack
from ..exception import JMCSyntaxException
from ..tokenizer import Token, TokenType, Tokenizer
from .utils import find_scoreboard_player_type, PlayerType

VAR_OPERATION_COMMANDS = JMCFunction.get_subclasses(
    FuncType.VARIABLE_OPERATION)


def variable_operation(
        tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack, is_execute: bool) -> str:
    """
    Parse statement for variable operation including custom JMC command that return and integer to be stored in scoreboard value

    :param tokens: Statement(List of tokens) for parsing
    :param tokenizer: Tokenizer
    :param datapack: Datapack object
    :param is_execute: Whether the statement/function is in `/execute`
    :return: Full minecraft command
    """
    if tokens[0].string.endswith('.get') and len(
            tokens) > 1 and tokens[1].token_type == TokenType.PAREN_ROUND:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                "Unexpected token", tokens[2], tokenizer)

        if tokens[1].string != "()":
            raise JMCSyntaxException(
                "'get' function takes no arguments, expected empty bracket ()", tokens[1], tokenizer)

        return f"scoreboard players get {tokens[0].string[:-4]} {DataPack.var_name}"

    if len(tokens) == 1:
        raise JMCSyntaxException(
            "Expected operator after variable", tokens[0], tokenizer, col_length=True)

    if tokens[1].token_type != TokenType.OPERATOR:
        raise JMCSyntaxException(
            f"Expected operator or 'matches' (got {tokens[1].token_type.value})", tokens[1], tokenizer)

    operator = tokens[1].string

    if operator in {'++', '--'}:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                f"Unexpected token ('{tokens[2].string}') after '{tokens[1].string}'", tokens[2], tokenizer)
        if operator == '++':
            return f"scoreboard players add {tokens[0].string} {DataPack.var_name} 1"
        if operator == '--':
            return f"scoreboard players remove {tokens[0].string} {DataPack.var_name} 1"
    elif operator in {'*=', '+=', '-=', '*=', '/=', '%=', '++', '--', '><', "->", '>', '<', '='}:
        if len(tokens) == 2:
            raise JMCSyntaxException(
                f"Expected keyword after operator{tokens[1].string} (got nothing)", tokens[1], tokenizer, suggestion="Expected integer or variable or target selector")
        if tokens[2].token_type != TokenType.KEYWORD:
            raise JMCSyntaxException(
                f"Expected keyword after operator{tokens[1].string} (got {tokens[2].token_type.value})", tokens[2], tokenizer, suggestion="Expected integer or variable or target selector")

        if operator == '=' and tokens[2].token_type == TokenType.KEYWORD and tokens[2].string in VAR_OPERATION_COMMANDS:
            if len(tokens) == 3:
                raise JMCSyntaxException(
                    "Expected round bracket '(' after variable operation function", tokens[2], tokenizer, col_length=True)

            if tokens[3].token_type != TokenType.PAREN_ROUND:
                raise JMCSyntaxException(
                    f"Expected round bracket '(' (got {tokens[3].string})", tokens[3], tokenizer, col_length=True)

            if len(tokens) > 4:
                raise JMCSyntaxException(
                    f"Unexpected token", tokens[4], tokenizer)

            return VAR_OPERATION_COMMANDS[tokens[2].string](
                tokens[3], datapack, tokenizer, var=tokens[0].string, is_execute=is_execute).call()

        left_token = tokens[0]
        right_token = tokens[2]
        # left_token.string operator right_token.string

        if len(tokens) > 3:
            if (  # If rvar is obj:selector
                len(tokens) == 5
                and
                tokens[3].token_type == TokenType.OPERATOR
                and
                tokens[3].string == ':'
                and
                tokens[4].token_type == TokenType.KEYWORD
            ):
                right_token = Token(
                    TokenType.KEYWORD,
                    tokens[2].line,
                    tokens[2].col,
                    tokens[2].string +
                    ':' +
                    tokens[4].string)
            else:
                raise JMCSyntaxException(
                    f"Unexpected token ('{tokens[3].string}') after variable ('{tokens[2].string}')", tokens[3], tokenizer)

        scoreboard_player = find_scoreboard_player_type(
            right_token, tokenizer, allow_integer=False)

        if operator == '->':
            if scoreboard_player.player_type == PlayerType.INTEGER:
                raise JMCSyntaxException(
                    "Cannot copy score into integer", right_token, tokenizer)
            if isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is int")

            return f"scoreboard players operation {scoreboard_player.value[1]} {scoreboard_player.value[0]} = {left_token.string} {DataPack.var_name}"

        if scoreboard_player.player_type == PlayerType.INTEGER:
            if operator == '+=':
                return f"scoreboard players add {left_token.string} {DataPack.var_name} {scoreboard_player.value}"
            if operator == '-=':
                return f"scoreboard players remove {left_token.string} {DataPack.var_name} {scoreboard_player.value}"
            if operator == '=':
                return f"scoreboard players set {left_token.string} {DataPack.var_name} {scoreboard_player.value}"

            if not isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is not int")
            datapack.add_int(scoreboard_player.value)
            return f"scoreboard players operation {left_token.string} {DataPack.var_name} {operator} {scoreboard_player.value} {DataPack.int_name}"

        if isinstance(scoreboard_player.value, int):
            raise ValueError("scoreboard_player.value is int")

        return f"scoreboard players operation {left_token.string} {DataPack.var_name} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}"

    raise JMCSyntaxException(
        f"Unrecognized operator ({operator})", tokens[1], tokenizer)
