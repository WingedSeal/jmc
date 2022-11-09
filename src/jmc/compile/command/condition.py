"""Module for parsing conditions (statements that return boolean), called from command/_flow_control.py and lexer.py"""

from dataclasses import dataclass
from typing import Union

from ..tokenizer import TokenType, Tokenizer, Token
from ..exception import JMCSyntaxException, JMCValueError
from ..datapack import DataPack
from .utils import find_scoreboard_player_type, PlayerType
from .jmc_function import JMCFunction, FuncType

from .builtin_function import bool_function

AND_OPERATOR = '&&'
OR_OPERATOR = '||'
NOT_OPERATOR = '!'

IF = True
UNLESS = False

VAR = '__logic__'
BOOL_FUNCTIONS = JMCFunction.get_subclasses(FuncType.BOOL_FUNCTION)
count = 0


@dataclass(eq=False, repr=True)
class Condition:
    """
    Dataclass for condition containing string representation(excluding if/unless) and whether it's for `if` or `unless`
    """
    __slots__ = 'string', 'if_unless'
    string: str
    if_unless: bool
    """`True` means 'if', `False` means 'unless'"""

    def reverse(self) -> None:
        self.if_unless = not self.if_unless

    def __str__(self) -> str:
        return f"{'if' if self.if_unless else 'unless'} {self.string}"


AST_TYPE = Union[dict[str,  # type: ignore
                      Union[str, list["AST_TYPE"], "AST_TYPE"]  # type: ignore
                      ],
                 Condition]


def merge_condition(conditions: list[Condition]) -> str:
    """
    Merge all condition into a single string for minecraft execute if

    :param conditions: List of conditions
    :return: Minecraft arguments after `execute if`
    """
    return ' '.join(str(condition) for condition in conditions)


def custom_condition(
        tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack) -> Condition:
    """
    Create a custom JMC condition from list of tokens representing statement

    :param tokens: List of tokens representing statement for condition
    :param tokenizer: Tokenizer
    :param datapack: Datapack object
    :return: Condition object parsed from list of tokens
    """
    if tokens[0].token_type == TokenType.KEYWORD and tokens[0].string.startswith(
            DataPack.VARIABLE_SIGN):
        tokens = tokenizer.split_keyword_tokens(tokens, ['>', '=', '<', '!'])
        first_token = tokens[0]
        for operator in ['===', '==',
                         '>=', '<=', '!=', '>', '<', '=']:  # sort key=len
            list_of_tokens = tokenizer.find_tokens(tokens, operator)
            if len(list_of_tokens) == 1:
                continue
            elif len(list_of_tokens) > 2:
                raise JMCSyntaxException(
                    f"Duplicated operator({operator}) in condition", list_of_tokens[2][-1], tokenizer)

            if len(list_of_tokens[0]) > 1:
                raise JMCSyntaxException(
                    f"Unexpected token ('{list_of_tokens[0][1].string}') after variable ('{list_of_tokens[0][0].string}') in condition", list_of_tokens[0][1], tokenizer, suggestion="Expected operator")

            if len(list_of_tokens[1]) > 1:
                raise JMCSyntaxException(
                    "Unexpected token in condition", list_of_tokens[1][-1], tokenizer)

            second_token = list_of_tokens[1][0]
            scoreboard_player = find_scoreboard_player_type(
                second_token, tokenizer)

            if scoreboard_player.player_type == PlayerType.INTEGER:
                if not isinstance(scoreboard_player.value, int):
                    raise ValueError("scoreboard_player.value is not int")
                compared = f'score {first_token.string} {DataPack.var_name} matches'
                if operator in {'===', '==', '='}:
                    return Condition(
                        f'{compared} {scoreboard_player.value}', IF)
                if operator == '>=':
                    return Condition(
                        f'{compared} {scoreboard_player.value}..', IF)
                if operator == '>':
                    return Condition(
                        f'{compared} {scoreboard_player.value+1}..', IF)
                if operator == '<=':
                    return Condition(
                        f'{compared} ..{scoreboard_player.value}', IF)
                if operator == '<':
                    return Condition(
                        f'{compared} ..{scoreboard_player.value-1}', IF)
            else:
                if operator == '!=':
                    if isinstance(scoreboard_player.value, int):
                        raise ValueError("scoreboard_player.value is int")
                    return Condition(
                        f'score {first_token.string} {DataPack.var_name} = {scoreboard_player.value[1]} {scoreboard_player.value[0]}', UNLESS)

                if operator in {'===', '==', '='}:
                    operator = '='

                if isinstance(scoreboard_player.value, int):
                    raise ValueError("scoreboard_player.value is int")
                return Condition(
                    f'score {first_token.string} {DataPack.var_name} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}', IF)
            break

        if tokens[1].token_type == TokenType.KEYWORD and tokens[1].string == 'matches':
            if len(tokens) > 3:
                raise JMCSyntaxException(
                    "Unexpected token in condition", tokens[3], tokenizer)
            if tokens[2].token_type != TokenType.KEYWORD:
                raise JMCSyntaxException(
                    "Expected keyword", tokens[2], tokenizer)

            match_tokens_ = tokenizer.split_keyword_token(tokens[2], '..')
            match_tokens = tokenizer.find_token(match_tokens_, '..')
            if len(match_tokens) != 2 or len(
                    match_tokens[0]) > 1 or len(match_tokens[1]) > 1:
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

            return Condition(
                f'score {first_token.string} {DataPack.var_name} matches {tokens[2].string}', IF)

        raise JMCSyntaxException(
            "Operator not found in custom condition", tokens[0], tokenizer)

    matched_function = BOOL_FUNCTIONS.get(
        tokens[0].string, None)
    if matched_function is not None:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                "Unexpected token", tokens[2], tokenizer, display_col_length=False)

        return Condition(
            *matched_function(tokens[1], datapack, tokenizer).call_bool())
    # End
    conditions: list[str] = []
    if tokens[0].string not in {"block", "blocks",
                                "data", "entity", "predicate", "score"}:
        raise JMCValueError(
            f"Unrecoginized condition '{tokens[0].string}'",
            tokens[0],
            tokenizer,
            suggestion="Consider using 'block' or 'blocks' or 'data' or 'entity' or 'predicate' or 'score'.")
    for token in tokens:
        if token.token_type == TokenType.PAREN_SQUARE:
            if not conditions:
                raise JMCSyntaxException(
                    "Unexpected square parenthesis []", token, tokenizer)
            conditions[-1] += token.string
        else:
            conditions.append(token.string)
    return Condition(' '.join(conditions), IF)


def find_operator(_tokens: list[Token], operator: str,
                  tokenizer: Tokenizer) -> list[list[Token]]:
    """
    Find sepecific operator in tokens and split them

    :param _tokens: List of tokens search
    :param operator: Operator to search for
    :param tokenizer: Tokenizer
    :return: List of (list of tokens)
    """
    list_of_tokens: list[list[Token]] = []
    tokens: list[Token] = []
    if _tokens[0].token_type == TokenType.KEYWORD and _tokens[0].string == operator:
        raise JMCSyntaxException(
            f"Unexpected operator ({operator})", _tokens[0], tokenizer)

    elif _tokens[-1].token_type == TokenType.KEYWORD and _tokens[-1].string == operator:
        raise JMCSyntaxException(
            f"Unexpected operator ({operator})", _tokens[-1], tokenizer)

    for token in _tokens:
        if token.token_type == TokenType.KEYWORD and token.string == operator:
            list_of_tokens.append(tokens)
            tokens = []
        else:
            tokens.append(token)
    list_of_tokens.append(tokens)
    return list_of_tokens


def condition_to_ast(
        tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack) -> AST_TYPE:
    """
    Turn condition in form of list of tokens to abstract syntax tree

    :param tokens: Condition in form of tokens
    :param tokenizer: Tokenizer
    :param datapack: Datapack object
    :raises JMCSyntaxException: Empty round parenthesis inside condition
    :return: Abstract syntax tree
    """
    if len(tokens) == 1 and tokens[0].token_type == TokenType.PAREN_ROUND:
        if tokens[0].string == '()':
            raise JMCSyntaxException(
                f"Empty round parenthesis () inside condition", tokens[0], tokenizer)

        tokenizer = Tokenizer(tokens[0].string[1:-1], tokenizer.file_path,
                              tokens[0].line, tokens[0].col + 1, tokenizer.file_string, expect_semicolon=False)
        tokens = tokenizer.programs[0]
    tokens = tokenizer.split_keyword_tokens(tokens, [OR_OPERATOR])
    list_of_tokens = find_operator(tokens, OR_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": OR_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer, datapack) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    tokens = tokenizer.split_keyword_tokens(tokens, [AND_OPERATOR])
    list_of_tokens = find_operator(tokens, AND_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": AND_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer, datapack) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    # NotOperator should have a body as either dict or string and not list
    tokens = tokenizer.split_keyword_tokens(tokens, [NOT_OPERATOR])
    if tokens[0].token_type == TokenType.KEYWORD and tokens[0].string == NOT_OPERATOR:
        return {"operator": NOT_OPERATOR, "body":
                condition_to_ast(tokens[1:], tokenizer, datapack)}

    return custom_condition(tokens, tokenizer, datapack)


def ast_to_commands(
        ast: AST_TYPE) -> tuple[list[Condition], list[tuple[list[Condition], int]] | None]:
    """
    Parse abstract syntax tree into list of conditions and list of commands that need to come before for it to works

    :param ast: Abstract syntax tree
    :raises ValueError: Invalid AST
    :return: A tuple of (
        A chain of conditions(List of Condition)

        Commands(
            List of Condition and n (`__logic__n` for minecraft function name)
        ) that need to come before (can be None)
    )
    """
    global count
    if isinstance(ast, Condition):
        return [ast], None

    if ast["operator"] == AND_OPERATOR:
        conditions: list[Condition] = []
        precommand_and: list[tuple[list[Condition], int]] = []
        for body in ast["body"]:  # type: ignore
            if isinstance(body, str):
                raise ValueError('ast["body"] is string')
            _conditions, precommand = ast_to_commands(body)  # noqa
            conditions.extend(_conditions)
            if precommand is not None:
                precommand_and.extend(precommand)
        return conditions, (precommand_and if precommand_and else None)

    elif ast["operator"] == OR_OPERATOR:
        _count = count
        count += 1
        precommand_or: list[tuple[list[Condition], int]] = []
        for body in ast["body"]:  # type: ignore
            if isinstance(body, str):
                raise ValueError('ast["body"] is string')
            conditions, precommand = ast_to_commands(body)
            if precommand is not None:
                precommand_or.extend(precommand)
            precommand_or.append((conditions, _count))

        return [Condition(
            f"score {VAR}{_count} {DataPack.var_name} matches 1", IF)], precommand_or

    elif ast["operator"] == NOT_OPERATOR:
        body = ast["body"]
        if not isinstance(ast["body"], Condition):
            raise ValueError('ast["body"] is noy Condition')
        conditions, precommand = ast_to_commands(ast["body"])
        for condition in conditions:
            condition.reverse()
        return conditions, precommand

    raise ValueError("Invalid AST")


def ast_to_strings(ast: AST_TYPE) -> tuple[str, str]:
    """
    Turns AST into tuple of full `execute if command` a multiple line string representing precommands

    :param ast: Abstract Syntax tree
    :return: tuple of `execute if` command(excluding `execute`) a multiple line string representing precommands
    """

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
                    f"scoreboard players set {VAR}{current_count} {DataPack.var_name} 0")
                precommands.append(
                    f"execute {merge_condition(conditions_and_count[0])} run scoreboard players set {VAR}{current_count} {DataPack.var_name} 1")
                continue

            precommands.append(
                f"execute unless score {VAR}{current_count} {DataPack.var_name} matches 1 {merge_condition(conditions_and_count[0])} run scoreboard players set {VAR}{current_count} {DataPack.var_name} 1")
        precommand = '\n'.join(precommands)

    condition_string = merge_condition(conditions)
    return condition_string, precommand


def parse_condition(condition_token: Token |
                    list[Token], tokenizer: Tokenizer, datapack: DataPack) -> tuple[str, str]:
    """
    Parse condition token(s) (token or list of tokens) to `if ...` and pre-commands with newline
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

    :param condition_token: Token or List of tokens
    :param tokenizer: Tokenizer
    :param datapack: Datapack object
    :return: tuple of `execute if` command(excluding `execute`) a multiple line string representing precommands
    """
    global count
    count = 0
    tokens = condition_token if isinstance(
        condition_token, list) else [condition_token]

    ast = condition_to_ast(tokens, tokenizer, datapack)
    condition, precommand = ast_to_strings(ast)
    precommand = precommand + '\n' if precommand else ""
    return condition, precommand
