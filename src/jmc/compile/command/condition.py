"""Module for parsing conditions (statements that return boolean), called from command/_flow_control.py and lexer.py"""

from dataclasses import dataclass, field
from typing import Union


from ...compile.utils import is_connected
from ..tokenizer import TokenType, Tokenizer, Token
from ..exception import JMCSyntaxException, JMCValueError
from ..datapack import DataPack
from .utils import find_scoreboard_player_type, PlayerType, is_obj_selector, merge_obj_selector
from .jmc_function import JMCFunction, FuncType

from .builtin_function import bool_function

AND_OPERATOR = "&&"
OR_OPERATOR = "||"
NOT_OPERATOR = "!"

IF = True
UNLESS = False

VAR = "__logic__"
BOOL_FUNCTIONS = JMCFunction.get_subclasses(FuncType.BOOL_FUNCTION)


@dataclass(eq=False, repr=True, slots=True)
class Condition:
    """
    Dataclass for condition containing string representation(excluding if/unless) and whether it's for `if` or `unless`
    """
    string: str
    if_unless: bool
    """`True` means 'if', `False` means 'unless'"""
    pre_commands: list[str] = field(default_factory=list)

    def reverse(self) -> None:
        """Reverse condition"""
        self.if_unless = not self.if_unless

    def __str__(self) -> str:
        return f"{'if' if self.if_unless else 'unless'} {self.string}"


AST_TYPE = dict[str,  # type: ignore
                      Union[str, list["AST_TYPE"], "AST_TYPE"]  # type: ignore
                ] | Condition


def merge_condition(conditions: list[Condition]) -> tuple[str, list[str]]:
    """
    Merge all condition into a single string for minecraft execute if

    :param conditions: List of conditions
    :return: A tuple of (Minecraft arguments after `execute if`) and (List of precommands in strings)
    """
    precommands: list[str] = []
    for condition in conditions:
        precommands.extend(condition.pre_commands)
    return (" ".join(str(condition) for condition in conditions), precommands)


def custom_condition(
        tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack) -> Condition:
    """
    Create a custom JMC condition from list of tokens representing statement

    :param tokens: List of tokens representing statement for condition
    :param tokenizer: Tokenizer
    :param datapack: Datapack object
    :return: Condition object parsed from list of tokens
    """

    if tokens[0].string.startswith(
            DataPack.VARIABLE_SIGN) or is_obj_selector(tokens):

        objective = DataPack.var_name
        if is_obj_selector(tokens):
            objective = tokens[0].string
            del tokens[0:2]
        if len(tokens) >= 2 and tokens[1].token_type == TokenType.PAREN_SQUARE:
            tokens[1] = tokenizer.merge_tokens(tokens[:2])
            del tokens[0]

        if len(tokens) == 1:
            return Condition(
                f"score {tokens[0].string} {objective} matches 1..", True)
        if len(tokens) == 2:
            raise JMCSyntaxException(
                f"Expected token after operator{tokens[1].string} in custom condition (got nothing)", tokens[0], tokenizer)

        if len(tokens) > 2 and is_obj_selector(tokens[2:]):
            tokens[2] = merge_obj_selector(tokens, tokenizer, datapack, 2)
        if len(tokens) > 3:
            if tokens[2].string == "-":
                tokens[2] = tokenizer.merge_tokens(tokens[2:4])
                del tokens[3]
            else:
                raise JMCSyntaxException(
                    f"Unexpected token ('{tokens[3].string}') after variable ('{tokens[2].string}') in condition", tokens[3], tokenizer)

        first_token, operator_token, second_token = tokens
        if operator_token.token_type == TokenType.OPERATOR:
            if second_token.string == "true":
                raise JMCSyntaxException(
                    "Expected integer, variable, or objective:selector", second_token, tokenizer,
                    suggestion=f"Did you mean `if ({first_token.string}) {{`?")
            if second_token.string == "false":
                raise JMCSyntaxException(
                    "Expected integer, variable, or objective:selector", second_token, tokenizer,
                    suggestion=f"Did you mean `if (!{first_token.string}) {{`?")
            scoreboard_player = find_scoreboard_player_type(
                second_token, tokenizer)
            operator = operator_token.string

            if scoreboard_player.player_type == PlayerType.INTEGER:
                if not isinstance(scoreboard_player.value, int):
                    raise ValueError("scoreboard_player.value is not int")
                compared = f'score {first_token.string} {objective} matches'
                if operator in {"===", "==", "="}:
                    return Condition(
                        f'{compared} {scoreboard_player.value}', IF)
                if operator in {"!=", "!=="}:
                    return Condition(
                        f'{compared} {scoreboard_player.value}', UNLESS)
                if operator == ">=":
                    return Condition(
                        f'{compared} {scoreboard_player.value}..', IF)
                if operator == ">":
                    return Condition(
                        f'{compared} {scoreboard_player.value+1}..', IF)
                if operator == "<=":
                    return Condition(
                        f'{compared} ..{scoreboard_player.value}', IF)
                if operator == "<":
                    return Condition(
                        f'{compared} ..{scoreboard_player.value-1}', IF)
                raise JMCSyntaxException(
                    f"Unrecognized operator ({operator})", operator_token, tokenizer)

            else:
                if operator == "!=":
                    if isinstance(scoreboard_player.value, int):
                        raise ValueError("scoreboard_player.value is int")
                    return Condition(
                        f'score {first_token.string} {objective} = {scoreboard_player.value[1]} {scoreboard_player.value[0]}', UNLESS)

                if operator in {"===", "==", "="}:
                    operator = '='

                if isinstance(scoreboard_player.value, int):
                    raise ValueError("scoreboard_player.value is int")
                return Condition(
                    f'score {first_token.string} {objective} {operator} {scoreboard_player.value[1]} {scoreboard_player.value[0]}', IF)

        elif operator_token.token_type == TokenType.KEYWORD and operator_token.string == "matches":
            match_tokens_ = tokenizer.split_keyword_token(tokens[2], "..")
            match_tokens = tokenizer.find_token(match_tokens_, "..")
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
                f'score {first_token.string} {objective} matches {tokens[2].string}', IF)

        else:
            raise JMCSyntaxException(
                f"Expected operator or 'matches' (got {tokens[1].token_type.value})", tokens[1], tokenizer)

    matched_function = BOOL_FUNCTIONS.get(
        tokens[0].string, None)
    if matched_function is not None:
        if len(tokens) > 2:
            raise JMCSyntaxException(
                "Unexpected token", tokens[2], tokenizer, display_col_length=False)

        return Condition(
            *matched_function(tokens[1], tokens[0], datapack, tokenizer, prefix="").call_bool())
    # End

    conditions: list[str] = []
    if tokens[0].string not in {"biome", "block", "blocks",
                                "data", "dimension", "entity",
                                "loaded", "predicate", "score"}:
        raise JMCValueError(
            f"Unrecognized condition '{tokens[0].string}'",
            tokens[0],
            tokenizer,
            suggestion="Consider using 'block' or 'blocks' or 'data' or 'entity' or 'predicate' or 'score'.")

    last_token = tokens[0]
    for token in tokens:
        if token.token_type == TokenType.PAREN_SQUARE:
            if not conditions:
                raise JMCSyntaxException(
                    "Unexpected square bracket, `[]`", token, tokenizer)
            conditions[-1] += token.string
        elif is_connected(
                token, last_token):
            conditions[-1] += token.string
        else:
            conditions.append(token.string)
        last_token = token
    return Condition(" ".join(conditions), IF)


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
    if _tokens[0].token_type == TokenType.OPERATOR and _tokens[0].string == operator:
        raise JMCSyntaxException(
            f"Unexpected operator ({operator})", _tokens[0], tokenizer)

    elif _tokens[-1].token_type == TokenType.OPERATOR and _tokens[-1].string == operator:
        raise JMCSyntaxException(
            f"Unexpected operator ({operator})", _tokens[-1], tokenizer)

    for token in _tokens:
        if token.token_type == TokenType.OPERATOR and token.string == operator:
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
    :raises JMCSyntaxException: Empty round bracket inside condition
    :return: Abstract syntax tree
    """
    if len(tokens) == 1 and tokens[0].token_type == TokenType.PAREN_ROUND:
        if tokens[0].string == "()":
            raise JMCSyntaxException(
                "Unexpected empty round bracket, `()`, inside condition", tokens[0], tokenizer)

        tokenizer = Tokenizer(tokens[0].string[1:-1], tokenizer.file_path,
                              tokens[0].line, tokens[0].col + 1, tokenizer.file_string, expect_semicolon=False)
        tokens = tokenizer.programs[0]
    list_of_tokens = find_operator(tokens, OR_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": OR_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer, datapack) for tokens in list_of_tokens]}

    list_of_tokens = find_operator(tokens, AND_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": AND_OPERATOR, "body": [
            condition_to_ast(tokens, tokenizer, datapack) for tokens in list_of_tokens]}

    # NotOperator should have a body as either dict or string and not list
    if tokens[0].token_type == TokenType.OPERATOR and tokens[0].string == NOT_OPERATOR:
        return {"operator": NOT_OPERATOR, "body":
                condition_to_ast(tokens[1:], tokenizer, datapack)}

    return custom_condition(tokens, tokenizer, datapack)


def ast_to_commands(
        ast: AST_TYPE, datapack: DataPack) -> tuple[list[Condition], list[tuple[list[Condition], int]] | None]:
    """
    Parse abstract syntax tree into list of conditions and list of commands that need to come before for it to works

    :param ast: Abstract syntax tree
    :raises ValueError: Invalid AST
    :return: A tuple of (
        A chain of conditions(List of Condition)
        and
        Commands(
            List of Condition and n (`__logic__n` for minecraft function name)
        ) that need to come before (can be None)
    )
    """
    if isinstance(ast, Condition):
        return [ast], None

    if ast["operator"] == AND_OPERATOR:
        conditions: list[Condition] = []
        precommand_and: list[tuple[list[Condition], int]] = []
        if isinstance(ast["body"], Condition):
            raise ValueError(
                'ast["body"] is a Condition instead of list in AND')
        for and_body in ast["body"]:
            if isinstance(and_body, str):
                raise ValueError('ast["body"] is string')
            _conditions, precommand = ast_to_commands(and_body, datapack)  # noqa
            conditions.extend(_conditions)
            if precommand is not None:
                precommand_and.extend(precommand)
        return conditions, (precommand_and if precommand_and else None)

    elif ast["operator"] == OR_OPERATOR:
        _count = datapack.data.condition_count
        datapack.data.condition_count += 1
        precommand_or: list[tuple[list[Condition], int]] = []
        if isinstance(ast["body"], Condition):
            raise ValueError(
                'ast["body"] is a Condition instead of list in OR')
        for or_body in ast["body"]:
            if isinstance(or_body, str):
                raise ValueError('ast["body"] is string')
            conditions, precommand = ast_to_commands(or_body, datapack)
            if precommand is not None:
                precommand_or.extend(precommand)
            precommand_or.append((conditions, _count))

        return [Condition(
            f"score {VAR}{_count} {DataPack.var_name} matches 1", IF)], precommand_or

    elif ast["operator"] == NOT_OPERATOR:
        if isinstance(ast["body"], Condition):
            conditions, precommand = ast_to_commands(ast["body"], datapack)
        elif isinstance(ast["body"], dict):
            if ast["body"]["operator"] == OR_OPERATOR:
                ast["body"]["operator"] = AND_OPERATOR
            elif ast["body"]["operator"] == AND_OPERATOR:
                ast["body"]["operator"] = OR_OPERATOR
            conditions, precommand = ast_to_commands(ast["body"], datapack)
        else:
            raise ValueError('ast["body"] is a list or str')
        for condition in conditions:
            condition.reverse()
        return conditions, precommand

    raise ValueError("Invalid AST")


def ast_to_strings(ast: AST_TYPE, datapack: DataPack) -> tuple[str, str]:
    """
    Turns AST into tuple of full `execute if command` a multiple line string representing precommands

    :param ast: Abstract Syntax tree
    :return: tuple of `execute if` command(excluding `execute`) a multiple line string representing precommands
    """

    conditions, precommand_conditions = ast_to_commands(ast, datapack)
    if precommand_conditions is None:
        precommand = ""
    else:
        precommands: list[str] = []
        current_count = -1
        for conditions_and_count in precommand_conditions:
            if conditions_and_count[1] > current_count:
                current_count += 1
                precommands.append(
                    f"scoreboard players set {VAR}{current_count} {DataPack.var_name} 0")
                merged_condition, merged_condition_pre_command = merge_condition(
                    conditions_and_count[0])
                precommands.extend(merged_condition_pre_command)
                precommands.append(
                    f"execute {merged_condition} run scoreboard players set {VAR}{current_count} {DataPack.var_name} 1")
                continue

            merged_condition, merged_condition_pre_command = merge_condition(
                conditions_and_count[0])
            precommands.extend(merged_condition_pre_command)
            precommands.append(
                f"execute unless score {VAR}{current_count} {DataPack.var_name} matches 1 {merged_condition} run scoreboard players set {VAR}{current_count} {DataPack.var_name} 1")
        precommand = "\n".join(precommands)

    condition_string, precommands_ = merge_condition(conditions)
    precommand += "\n".join(precommands_)
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
    datapack.data.condition_count = 0
    tokens = condition_token if isinstance(
        condition_token, list) else [condition_token]

    ast = condition_to_ast(tokens, tokenizer, datapack)
    condition, precommand = ast_to_strings(ast, datapack)
    precommand = precommand + "\n" if precommand else ""
    return condition, precommand
