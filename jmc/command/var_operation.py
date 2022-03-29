from ..datapack import DataPack
from ..exception import JMCSyntaxException
from ..tokenizer import Token, Tokenizer
from .utils import find_scoreboard_player_type, PlayerType

NEW_LINE = '\n'


def variable_operation(tokens: list[Token], tokenizer: Tokenizer) -> str:
    tokens = tokenizer.split_tokens(tokens, ['-', '=', '+', '*', '%'])
    for operator in ['*=', '+=', '-=', '*=', '/=', '%=', '++', '--']:  # sort key=len
        list_of_tokens = tokenizer.find_tokens(tokens, operator)
        if len(list_of_tokens) == 1:
            continue

        if len(list_of_tokens) > 2:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nDuplicated operator({operator}) in condition at line {list_of_tokens[2][-1].line} col {list_of_tokens[2][-1].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[2][-1].line-1][:list_of_tokens[2][-1].col + list_of_tokens[2][-1].length - 1]} <-")

        if operator in ['++', '--']:
            if list_of_tokens[1]:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nUnexpected token after `++` at line {list_of_tokens[1][0].line} col {list_of_tokens[1][0].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[1][0].line-1][:list_of_tokens[1][0].col+list_of_tokens[1][0].length-1]} <-"
                )
            if len(list_of_tokens[0]) > 1:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nUnexpected token after `++` at line {list_of_tokens[0][1].line} col {list_of_tokens[0][1].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[0][1].line-1][:list_of_tokens[0][1].col+list_of_tokens[0][1].length-1]} <-"
                )

            if operator == '++':
                return f"scoreboard players add {list_of_tokens[0][0]} {DataPack.VAR_NAME} 1"
            if operator == '--':
                return f"scoreboard players remove {list_of_tokens[0][0]} {DataPack.VAR_NAME} 1"

        if operator in ['+=', '-=', '=']:
            return "NOT IMPLEMENTED"

        if operator in ['*=', '/=', '%=']:
            return "NOT IMPLEMENTED"

        break

    raise JMCSyntaxException(
        f"In {tokenizer.file_path}\nUnexpected token in condition at line {tokens[0].line} col {tokens[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[tokens[0].line-1][:tokens[0].col + tokens[0].length - 1]} <-")
