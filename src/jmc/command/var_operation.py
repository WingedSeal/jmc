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

    tokens = tokenizer.split_tokens(
        tokens, ['-', '=', '+', '*', '%', '>', '<'])
    if len(tokens) == 1:
        raise JMCSyntaxException(
            "Expected operator after variable", tokens[0], tokenizer, col_length=True)

    for operator in ['*=', '+=', '-=', '*=', '/=', '%=',
                     '++', '--', '><', "->", '>', '<', '=']:  # sort key=len
        list_of_tokens = tokenizer.find_tokens(tokens, operator)
        if len(list_of_tokens) == 1:
            continue

        if len(list_of_tokens) > 2:
            raise JMCSyntaxException(
                f"Duplicated operator({operator})", list_of_tokens[2][-1], tokenizer)

        if operator in {'++', '--'}:
            if list_of_tokens[1]:
                raise JMCSyntaxException(
                    f"Unexpected token after '{operator}'", list_of_tokens[1][0], tokenizer)
            if len(list_of_tokens[0]) > 1:
                raise JMCSyntaxException(
                    f"Unexpected token before '{operator}'", list_of_tokens[0][1], tokenizer)

            if operator == '++':
                return f"scoreboard players add {list_of_tokens[0][0].string} {DataPack.var_name} 1"
            if operator == '--':
                return f"scoreboard players remove {list_of_tokens[0][0].string} {DataPack.var_name} 1"

        if operator == '=' and list_of_tokens[1][0].token_type == TokenType.KEYWORD and list_of_tokens[1][0].string in VAR_OPERATION_COMMANDS:
            if len(list_of_tokens[1]) == 1:
                raise JMCSyntaxException(
                    "Expected (", list_of_tokens[1][0], tokenizer, col_length=True)

            if list_of_tokens[1][1].token_type != TokenType.PAREN_ROUND:
                raise JMCSyntaxException(
                    "Expected (", list_of_tokens[1][1], tokenizer)

            if len(list_of_tokens[1]) > 2:
                raise JMCSyntaxException(
                    "Unexpected token", list_of_tokens[1][2], tokenizer)

            return VAR_OPERATION_COMMANDS[list_of_tokens[1][0].string](
                list_of_tokens[1][1], datapack, tokenizer, var=list_of_tokens[0][0].string, is_execute=is_execute).call()

        if len(list_of_tokens[1]) > 1:
            raise JMCSyntaxException(
                f"Unexpected token ({list_of_tokens[1][1].string})", list_of_tokens[1][1], tokenizer)

        scoreboard_player = find_scoreboard_player_type(
            list_of_tokens[1][0], tokenizer, allow_integer=False)

        if operator == '->':
            if scoreboard_player.player_type == PlayerType.INTEGER:
                raise JMCSyntaxException(
                    "Cannot copy score into integer", list_of_tokens[1][0], tokenizer)
            if isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is int")

            return f"scoreboard players operation {scoreboard_player.value[1]} {scoreboard_player.value[0]} = {list_of_tokens[0][0].string} {DataPack.var_name}"

        if scoreboard_player.player_type == PlayerType.INTEGER:
            if operator == '+=':
                return f"scoreboard players add {list_of_tokens[0][0].string} {DataPack.var_name} {scoreboard_player.value}"
            if operator == '-=':
                return f"scoreboard players remove {list_of_tokens[0][0].string} {DataPack.var_name} {scoreboard_player.value}"
            if operator == '=':
                return f"scoreboard players set {list_of_tokens[0][0].string} {DataPack.var_name} {scoreboard_player.value}"

            if not isinstance(scoreboard_player.value, int):
                raise ValueError("scoreboard_player.value is not int")
            datapack.ints.add(scoreboard_player.value)
            return f"scoreboard players operation {list_of_tokens[0][0].string} {DataPack.var_name} {operator} {scoreboard_player.value} {DataPack.int_name}"

        if isinstance(scoreboard_player.value, int):
            raise ValueError("scoreboard_player.value is int")

        return f"scoreboard players operation {list_of_tokens[0][0].string} {DataPack.var_name} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}"

    raise JMCSyntaxException(
        "No operator found in variable operation", tokens[0], tokenizer)
