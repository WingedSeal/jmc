from dataclasses import dataclass
from typing import Optional, Union

from ..tokenizer import TokenType, Tokenizer, Token
from ..exception import JMCSyntaxException
from ..datapack import DataPack
from .utils import find_scoreboard_player_type, PlayerType

NEW_LINE = '\n'

AND_OPERATOR = '&&'
OR_OPERATOR = '||'
NOT_OPERATOR = '!'

IF = True
UNLESS = False

VAR = '__logic__'

count = 0


@dataclass(eq=False, repr=True)
class Condition:
    string: str
    if_unless: bool
    """`True` means 'if', `False` means 'unless'"""

    def reverse(self) -> None:
        self.if_unless = not self.if_unless

    def __str__(self) -> str:
        return f"{'if' if self.if_unless else 'unless'} {self.string}"


def merge_condition(conditions: list[Condition]) -> str:
    return ' '.join(str(condition) for condition in conditions)


def custom_condition(tokens: list[Token], tokenizer: Tokenizer) -> str:
    if tokens[0].token_type == TokenType.keyword and tokens[0].string.startswith(DataPack.VARIABLE_SIGN):
        tokens = tokenizer.split_tokens(tokens, ['>', '=', '<'])
        for operator in ['===', '==', '>=', '<=', '>', '<', '=']:  # sort key=len
            list_of_tokens = tokenizer.find_tokens(tokens, operator)
            if len(list_of_tokens) == 1:
                continue
            elif len(list_of_tokens) > 2:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nDuplicated operator({operator}) in condition at line {list_of_tokens[2][-1].line} col {list_of_tokens[2][-1].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[2][-1].line-1][:list_of_tokens[2][-1].col + list_of_tokens[2][-1].length - 1]} <-")

            if len(list_of_tokens[1]) > 1:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nUnexpected token in condition at line {list_of_tokens[1][-1].line} col {list_of_tokens[1][-1].col}.\n{tokenizer.file_string.split(NEW_LINE)[list_of_tokens[1][-1].line-1][:list_of_tokens[1][-1].col + list_of_tokens[1][-1].length - 1]} <-")
            second_token = list_of_tokens[1][0]
            scoreboard_player = find_scoreboard_player_type(
                second_token, tokenizer)

            if scoreboard_player.player_type == PlayerType.integer:
                compared = f'score {list_of_tokens[0][0].string} {DataPack.VAR_NAME} matches'
                if operator in ['===', '==', '=']:
                    return f'{compared} {scoreboard_player.value}'
                if operator == '>=':
                    return f'{compared} {scoreboard_player.value}..'
                if operator == '>':
                    return f'{compared} {scoreboard_player.value+1}..'
                if operator == '<=':
                    return f'{compared} ..{scoreboard_player.value}'
                if operator == '<':
                    return f'{compared} ..{scoreboard_player.value-1}'
            else:
                if operator in {'===', '==', '='}:
                    operator = '='
                return f'score {list_of_tokens[0][0].string} {DataPack.VAR_NAME} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}'
            break

        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nUnexpected token in condition at line {tokens[0].line} col {tokens[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[tokens[0].line-1][:tokens[0].col + tokens[0].length - 1]} <-")
    # End
    conditions: list[str] = []
    for token in tokens:
        if token.token_type == TokenType.paren_square:
            if not conditions:
                raise JMCSyntaxException(
                    f"In {tokenizer.file_path}\nUnexpected square parenthesis [] at line {token.line} col {token.col}.\n{tokenizer.file_string.split(NEW_LINE)[token.line-1][:token.col + token.length - 1]} <-")
            conditions[-1] += token.string
        else:
            conditions.append(token.string)
    return ' '.join(conditions)


def find_operator(_tokens: list[Token], operator: str, tokenizer: Tokenizer) -> list[list[Token]]:
    list_of_tokens = []
    tokens: list[str] = []
    if _tokens[0].token_type == TokenType.keyword and _tokens[0].string == operator:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nUnexpected operator {operator} at line {_tokens[0].line} col {_tokens[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[_tokens[0].line-1][:_tokens[0].col + _tokens[0].length]} <-")
    elif _tokens[-1].token_type == TokenType.keyword and _tokens[-1].string == operator:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nUnexpected operator {operator} at line {_tokens[-1].line} col {_tokens[-1].col}.\n{tokenizer.file_string.split(NEW_LINE)[_tokens[-1].line-1][:_tokens[-1].col + _tokens[-1].length]} <-")

    for token in _tokens:
        if token.token_type == TokenType.keyword and token.string == operator:
            list_of_tokens.append(tokens)
            tokens = []
        else:
            tokens.append(token)
    list_of_tokens.append(tokens)
    return list_of_tokens


def condition_to_ast(tokens: list[Token], tokenizer: Tokenizer) -> Union[dict, str]:
    if len(tokens) == 1 and tokens[0].token_type == TokenType.paren_round:
        if tokens[0].string == '()':
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nEmpty round parenthesis () inside condition at line {tokens[0].line} col {tokens[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[tokens[0].line-1][:tokens[0].col + tokens[0].length - 1]} <-")
        tokenizer = Tokenizer(tokens[0].string[1:-1], tokenizer.file_path,
                              tokens[0].line, tokens[0].col, tokenizer.file_string, expect_semicolon=False)
        tokens = tokenizer.programs[0]
    tokens = tokenizer.split_tokens(tokens, [OR_OPERATOR])
    list_of_tokens = find_operator(tokens, OR_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": OR_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    tokens = tokenizer.split_tokens(tokens, [AND_OPERATOR])
    list_of_tokens = find_operator(tokens, AND_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": AND_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    # NotOperator should have a body as either dict or string and not list
    tokens = tokenizer.split_tokens(tokens, [NOT_OPERATOR])
    if tokens[0].token_type == TokenType.keyword and tokens[0].string == NOT_OPERATOR:
        return {"operator": NOT_OPERATOR, "body":
                condition_to_ast(tokens[1:], tokenizer)}

    return custom_condition(tokens, tokenizer)


def ast_to_commands(ast: Union[dict, str]) -> tuple[list[Condition], Optional[list[tuple[list[Condition], int]]]]:
    global count
    if isinstance(ast, str):
        return [Condition(ast, IF)], None

    if ast["operator"] == AND_OPERATOR:
        conditions: list[Condition] = []
        precommand_conditions: list[tuple[list[Condition], int]] = []
        for body in ast["body"]:
            condition, _precommand_conditions = ast_to_commands(body)  # noqa
            conditions.extend(condition)
            if _precommand_conditions is not None:
                precommand_conditions.extend(_precommand_conditions)
        if not precommand_conditions:
            precommand_conditions = None
        return conditions, precommand_conditions

    if ast["operator"] == OR_OPERATOR:
        _count = count
        count += 1
        precommand_conditions: list[tuple[list[Condition], int]] = []
        for body in ast["body"]:
            condition, _precommand_conditions = ast_to_commands(body)
            if _precommand_conditions is not None:
                precommand_conditions.extend(_precommand_conditions)
            precommand_conditions.append((condition, _count))

        return [Condition(f"score {VAR}{_count} {DataPack.VAR_NAME} matches 1", IF)], precommand_conditions

    if ast["operator"] == NOT_OPERATOR:
        conditions, _precommand_conditions = ast_to_commands(ast["body"])
        for condition in conditions:
            condition.reverse()
        return conditions, _precommand_conditions

    raise ValueError("Invalid AST")


def commands_to_strings(ast: Union[dict, str]) -> tuple[str, str]:

    conditions, precommand_conditions = ast_to_commands(ast)
    if precommand_conditions is None:
        precommand = ""
    else:
        precommands = []
        current_count = -1
        for conditions_and_count in precommand_conditions:
            if conditions_and_count[1] > current_count:
                current_count += 1
                precommands.append(
                    f"scoreboard players reset {VAR}{current_count} {DataPack.VAR_NAME}")
                precommands.append(
                    f"execute {merge_condition(conditions_and_count[0])} run scoreboards players set {VAR}{current_count} {DataPack.VAR_NAME} 1")
                continue

            precommands.append(
                f"execute unless score {VAR}{current_count} {DataPack.VAR_NAME} matches 1 {merge_condition(conditions_and_count[0])} run scoreboards players set {VAR}{current_count} {DataPack.VAR_NAME} 1")
        precommand = '\n'.join(precommands)

    condition_string = merge_condition(conditions)
    return condition_string, precommand


def parse_condition(condition_token: Token, tokenizer: Tokenizer) -> tuple[str, str]:
    """Return `if ...` and pre-commands with newline
Example:
```py
condition1, precommands1 = parse_condition(...)
condition2, precommands2 = parse_condition(...)
commands = [
    f"{precommands1}execute {condition1} run {datapack.add_private_function("if_else", token, tokenizer)}",
    f"{precommands2}execute unless ... {condition2} run {datapack.add_private_function("if_else", token, tokenizer)}",
]
return datapack.add_raw_private_function("if_else", commands)
```
"""
    global count
    count = 0
    ast = condition_to_ast([condition_token], tokenizer)
    condition, precommand = commands_to_strings(ast)
    precommand = precommand+'\n' if precommand else ""
    return condition, precommand
