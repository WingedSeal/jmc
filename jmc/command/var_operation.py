from ..datapack import DataPack
from ..exception import JMCSyntaxException
from ..tokenizer import Token, TokenType, Tokenizer
from .utils import find_scoreboard_player_type, PlayerType

NEW_LINE = '\n'


def variable_operation(tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack) -> str:
    if len(tokens) == 1:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected operator after variable at line {tokens[0].line} col {tokens[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[tokens[0].line-1][:tokens[0].col + tokens[0].length - 1]} <-")

    if tokens[0].string.endswith('.get') and tokens[1].token_type == TokenType.paren_round:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nUnexpected token at line {tokens[2].line} col {tokens[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[tokens[2].line-1][:tokens[2].col + tokens[2].length - 2]} <-")
        if tokens[1].string != "()":
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\n`get` function takes no arguments, expected empty bracket () at line {tokens[1].line} col {tokens[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[tokens[1].line-1][:tokens[1].col + tokens[1].length - 1]} <-")
        return f"scoreboard players get {tokens[0].string[:-4]} {DataPack.VAR_NAME}"

    tokens = tokenizer.split_tokens(
        tokens, ['-', '=', '+', '*', '%', '>', '<'])
    for operator in ['*=', '+=', '-=', '*=', '/=', '%=', '++', '--', '><', "->", '>', '<', '=']:  # sort key=len
        list_of_tokens = tokenizer.find_tokens(tokens, operator)
        if len(list_of_tokens) == 1:
            continue

        if len(list_of_tokens) > 2:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nDuplicated operator({operator}) at line {list_of_tokens[2][-1].line} col {list_of_tokens[2][-1].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[2][-1].line-1][:list_of_tokens[2][-1].col + list_of_tokens[2][-1].length - 1]} <-")

        if operator in ['++', '--']:
            if list_of_tokens[1]:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nUnexpected token after `++` at line {list_of_tokens[1][0].line} col {list_of_tokens[1][0].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[1][0].line-1][:list_of_tokens[1][0].col+list_of_tokens[1][0].length-1]} <-"
                )
            if len(list_of_tokens[0]) > 1:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nUnexpected token after `--` at line {list_of_tokens[0][1].line} col {list_of_tokens[0][1].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[0][1].line-1][:list_of_tokens[0][1].col+list_of_tokens[0][1].length-1]} <-"
                )

            if operator == '++':
                return f"scoreboard players add {list_of_tokens[0][0].string} {DataPack.VAR_NAME} 1"
            if operator == '--':
                return f"scoreboard players remove {list_of_tokens[0][0].string} {DataPack.VAR_NAME} 1"

        if len(list_of_tokens[1]) > 1:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nUnexpected token ({list_of_tokens[1][1]}) at line {list_of_tokens[1][1].line} col {list_of_tokens[1][1].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[1][1].line-1][:list_of_tokens[1][1].col+list_of_tokens[1][1].length-1]} <-"
            )

        scoreboard_player = find_scoreboard_player_type(
            list_of_tokens[1][0], tokenizer)

        if operator == '->':
            if scoreboard_player.player_type == PlayerType.integer:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nCannot copy score into integer at line {list_of_tokens[1][0].line} col {list_of_tokens[1][0].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[1][0].line-1][:list_of_tokens[1][0].col + list_of_tokens[1][0].length - 1]} <-")
            return f"scoreboard players operation {scoreboard_player.value[1]} {scoreboard_player.value[0]} = {list_of_tokens[0][0].string} {DataPack.VAR_NAME}"

        if scoreboard_player.player_type == PlayerType.integer:
            if operator == '+=':
                return f"scoreboard players add {list_of_tokens[0][0].string} {DataPack.VAR_NAME} {scoreboard_player.value}"
            if operator == '-=':
                return f"scoreboard players remove {list_of_tokens[0][0].string} {DataPack.VAR_NAME} {scoreboard_player.value}"
            if operator == '=':
                return f"scoreboard players set {list_of_tokens[0][0].string} {DataPack.VAR_NAME} {scoreboard_player.value}"

            datapack.ints.add(scoreboard_player.value)
            return f"scoreboard players operation {list_of_tokens[0][0].string} {DataPack.VAR_NAME} {operator} {scoreboard_player.value} {DataPack.INT_NAME}"

        return f"scoreboard players operation {list_of_tokens[0][0].string} {DataPack.VAR_NAME} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}"

    raise JMCSyntaxException(
        f"In {tokenizer.file_path}\nUnexpected token(No operator found) at line {tokens[0].line} col {tokens[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[tokens[0].line-1][:tokens[0].col + tokens[0].length - 1]} <-")
