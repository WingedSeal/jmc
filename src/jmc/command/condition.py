from dataclasses import dataclass
from typing import Optional, Union

from ..tokenizer import TokenType, Tokenizer, Token
from ..exception import JMCSyntaxException
from ..datapack import DataPack
from .utils import find_scoreboard_player_type, PlayerType
from .jmc_function import JMCFunction, FuncType

AND_OPERATOR = '&&'
OR_OPERATOR = '||'
NOT_OPERATOR = '!'

IF = True
UNLESS = False

VAR = '__logic__'
BOOL_FUNCTIONS = JMCFunction._get(FuncType.bool_function)
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


AST_TYPE = Union["AST_TYPE", Condition]


def merge_condition(conditions: list[Condition]) -> str:
    return ' '.join(str(condition) for condition in conditions)


def custom_condition(tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack) -> Condition:
    if tokens[0].token_type == TokenType.keyword and tokens[0].string.startswith(DataPack.VARIABLE_SIGN):
        tokens = tokenizer.split_tokens(tokens, ['>', '=', '<', '!'])
        first_token = tokens[0]
        for operator in ['===', '==', '>=', '<=', '!=', '>', '<', '=']:  # sort key=len
            list_of_tokens = tokenizer.find_tokens(tokens, operator)
            if len(list_of_tokens) == 1:
                continue
            elif len(list_of_tokens) > 2:
                raise JMCSyntaxException(
                    f"Duplicated operator({operator}) in condition", list_of_tokens[2][-1], tokenizer)

            if len(list_of_tokens[1]) > 1:
                raise JMCSyntaxException(
                    "Unexpected token in condition", list_of_tokens[1][-1], tokenizer)

            second_token = list_of_tokens[1][0]
            scoreboard_player = find_scoreboard_player_type(
                second_token, tokenizer)

            if scoreboard_player.player_type == PlayerType.integer:
                compared = f'score {first_token.string} {DataPack.VAR_NAME} matches'
                if operator in {'===', '==', '='}:
                    return Condition(f'{compared} {scoreboard_player.value}', IF)
                if operator == '>=':
                    return Condition(f'{compared} {scoreboard_player.value}..', IF)
                if operator == '>':
                    return Condition(f'{compared} {scoreboard_player.value+1}..', IF)
                if operator == '<=':
                    return Condition(f'{compared} ..{scoreboard_player.value}', IF)
                if operator == '<':
                    return Condition(f'{compared} ..{scoreboard_player.value-1}', IF)
            else:
                if operator == '!=':
                    return Condition(f'score {first_token.string} {DataPack.VAR_NAME} = {scoreboard_player.value[1]} {scoreboard_player.value[0]}', UNLESS)

                if operator in {'===', '==', '='}:
                    operator = '='
                return Condition(f'score {first_token.string} {DataPack.VAR_NAME} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}', IF)
            break

        if tokens[1].token_type == TokenType.keyword and tokens[1].string == 'matches':
            if len(tokens) > 3:
                raise JMCSyntaxException(
                    "Unexpected token in condition", tokens[3], tokenizer)
            if tokens[2].token_type != TokenType.keyword:
                raise JMCSyntaxException(
                    "Expected keyword", tokens[2], tokenizer)

            match_tokens = tokenizer.split_token(tokens[2], '..')
            match_tokens = tokenizer.find_token(match_tokens, '..')
            if len(match_tokens) != 2 or len(match_tokens[0]) > 1 or len(match_tokens[1]) > 1:
                raise JMCSyntaxException(
                    "Expected <integer>..<integer> after 'matches'", tokens[2], tokenizer)
            if not match_tokens[0]:
                raise JMCSyntaxException(
                    "Expected <integer>..<integer> after 'matches'", tokens[2], tokenizer, suggestion=f"Use {first_token.string}<={match_tokens[1][0].string} instead")
            if not match_tokens[1]:
                raise JMCSyntaxException(
                    "Expected <integer>..<integer> after 'matches'", tokens[2], tokenizer, suggestion=f"Use {first_token.string}>={match_tokens[0][0].string} instead")

            first_int = int(match_tokens[0][0].string)
            second_int = int(match_tokens[1][0].string)
            if first_int == second_int:
                raise JMCSyntaxException(
                    "First integer must not equal second integer after 'matches'", tokens[2], tokenizer, suggestion=f"Use {first_token.string}=={match_tokens[0][0].string} instead")
            if first_int > second_int:
                raise JMCSyntaxException(
                    "First integer must be less than second integer after 'matches'", tokens[2], tokenizer, suggestion=f"Did you mean {match_tokens[1][0].string}..{match_tokens[0][0].string} ?")

            return Condition(f'score {first_token.string} {DataPack.VAR_NAME} matches {tokens[2].string}', IF)

        raise JMCSyntaxException(
            "Operator not found in custom condition", tokens[0], tokenizer)

    matched_function = BOOL_FUNCTIONS.get(
        tokens[0].string, None)
    if matched_function is not None:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                "Unexpected token", tokens[2], tokenizer, display_col_length=False)

        return Condition(*matched_function(tokens[1], datapack, tokenizer).call())
    # End
    conditions: list[str] = []
    for token in tokens:
        if token.token_type == TokenType.paren_square:
            if not conditions:
                raise JMCSyntaxException(
                    "Unexpected square parenthesis []", token, tokenizer)
            conditions[-1] += token.string
        else:
            conditions.append(token.string)
    return Condition(' '.join(conditions), IF)


def find_operator(_tokens: list[Token], operator: str, tokenizer: Tokenizer) -> list[list[Token]]:
    list_of_tokens = []
    tokens: list[str] = []
    if _tokens[0].token_type == TokenType.keyword and _tokens[0].string == operator:
        raise JMCSyntaxException(
            f"Unexpected operator ({operator})", _tokens[0], tokenizer)

    elif _tokens[-1].token_type == TokenType.keyword and _tokens[-1].string == operator:
        raise JMCSyntaxException(
            f"Unexpected operator ({operator})", _tokens[-1], tokenizer)

    for token in _tokens:
        if token.token_type == TokenType.keyword and token.string == operator:
            list_of_tokens.append(tokens)
            tokens = []
        else:
            tokens.append(token)
    list_of_tokens.append(tokens)
    return list_of_tokens


def condition_to_ast(tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack) -> AST_TYPE:
    if len(tokens) == 1 and tokens[0].token_type == TokenType.paren_round:
        if tokens[0].string == '()':
            raise JMCSyntaxException(
                f"Empty round parenthesis () inside condition", tokens[0], tokenizer)

        tokenizer = Tokenizer(tokens[0].string[1:-1], tokenizer.file_path,
                              tokens[0].line, tokens[0].col+1, tokenizer.file_string, expect_semicolon=False)
        tokens = tokenizer.programs[0]
    tokens = tokenizer.split_tokens(tokens, [OR_OPERATOR])
    list_of_tokens = find_operator(tokens, OR_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": OR_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer, datapack) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    tokens = tokenizer.split_tokens(tokens, [AND_OPERATOR])
    list_of_tokens = find_operator(tokens, AND_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": AND_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer, datapack) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    # NotOperator should have a body as either dict or string and not list
    tokens = tokenizer.split_tokens(tokens, [NOT_OPERATOR])
    if tokens[0].token_type == TokenType.keyword and tokens[0].string == NOT_OPERATOR:
        return {"operator": NOT_OPERATOR, "body":
                condition_to_ast(tokens[1:], tokenizer, datapack)}

    return custom_condition(tokens, tokenizer, datapack)


def ast_to_commands(ast: AST_TYPE) -> tuple[list[Condition], Optional[list[tuple[list[Condition], int]]]]:
    global count
    if isinstance(ast, Condition):
        return [ast], None

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


def commands_to_strings(ast: AST_TYPE) -> tuple[str, str]:

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


def parse_condition(condition_token: Union[Token, list[Token]], tokenizer: Tokenizer, datapack: DataPack) -> tuple[str, str]:
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
    tokens = condition_token if isinstance(
        condition_token, list) else [condition_token]

    ast = condition_to_ast(tokens, tokenizer, datapack)
    condition, precommand = commands_to_strings(ast)
    precommand = precommand+'\n' if precommand else ""
    return condition, precommand
