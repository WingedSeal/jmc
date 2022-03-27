from textwrap import indent
from typing import Union
from ..tokenizer import TokenType, Tokenizer, Token
from ..exception import JMCSyntaxException

NEW_LINE = '\n'
AND_OPERATOR = '&&'
OR_OPERATOR = '||'
NOT_OPERATOR = '!'


def custom_condition(tokens: list[Token], tokenizer: Tokenizer) -> str:
    if tokens[0].token_type == TokenType.keyword and tokens[0].string.startswith('$'):
        tokens = tokenizer.split_tokens(tokens, ['>', '=', '<'])
        # TODO: IMPLEMENT CUSTOM CONDITION
        return "CUSTOM_CONDITION " + ' '.join([token.string for token in tokens])
    conditions = []
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
    tokens = []
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


def __parse_condition(tokens: list[Token], tokenizer: Tokenizer) -> Union[dict, str]:
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
            __parse_condition(tokens, tokenizer) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    tokens = tokenizer.split_tokens(tokens, [AND_OPERATOR])
    list_of_tokens = find_operator(tokens, AND_OPERATOR, tokenizer)
    if len(list_of_tokens) > 1:
        return {"operator": AND_OPERATOR, "body": [
            __parse_condition(tokens, tokenizer) for tokens in list_of_tokens]}
    else:
        tokens = list_of_tokens[0]

    # NotOperator should have a body as either dict or string and not list
    tokens = tokenizer.split_tokens(tokens, [NOT_OPERATOR])
    if tokens[0].token_type == TokenType.keyword and tokens[0].string == NOT_OPERATOR:
        return {"operator": AND_OPERATOR, "body":
                __parse_condition(tokens[1:], tokenizer)}

    return custom_condition(tokens, tokenizer)


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
    condition_dict = __parse_condition([condition_token], tokenizer)
    from json import dumps
    print(dumps(condition_dict, indent=2))
