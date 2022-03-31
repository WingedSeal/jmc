from typing import Optional


from .condition import parse_condition
from .utils import ScoreboardPlayer, find_scoreboard_player_type, PlayerType
from ..tokenizer import Token, Tokenizer, TokenType
from ..datapack import DataPack
from ..exception import JMCSyntaxException

NEW_LINE = '\n'


def if_(command: list[Token], datapack: DataPack, tokenizer: Tokenizer) -> None:
    if len(command) < 2:
        raise JMCSyntaxException(
            "Expected (", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.paren_round:
        raise JMCSyntaxException(
            "Expected (", command[1], tokenizer, display_col_length=False)
    if len(command) < 3:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, col_length=True)
    if command[2].token_type != TokenType.paren_curly:
        raise JMCSyntaxException(
            "Expected {", command[2], tokenizer, display_col_length=False)

    datapack.lexer.if_else_box.append((command[1], command[2]))


def else_(command: list[Token], datapack: DataPack, tokenizer: Tokenizer) -> Optional[str]:
    if not datapack.lexer.if_else_box:
        raise JMCSyntaxException(
            "'else' cannot be used without 'if'", command[0], tokenizer)

    if len(command) < 2:
        raise JMCSyntaxException(
            "Expected 'if' or {", command[0], tokenizer, col_length=True)

    if command[1].token_type == TokenType.keyword and command[1].string == 'if':
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected (", command[1], tokenizer, col_length=True)
        if command[2].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                "Expected (", command[2], tokenizer, display_col_length=False)
        if len(command) < 4:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, col_length=True)
        if command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                "Expected {", command[3], tokenizer, display_col_length=False)

        datapack.lexer.if_else_box.append(
            (command[2], command[3]))
    elif command[1].token_type == TokenType.paren_curly:
        datapack.lexer.if_else_box.append(
            (None, command[1])
        )
        return datapack.lexer.parse_if_else(tokenizer)
    else:
        raise JMCSyntaxException(
            "Expected 'if' or {", command[1], tokenizer, display_col_length=False)


def while_(command: list[Token], datapack: "DataPack", tokenizer: "Tokenizer") -> str:
    NAME = 'while'
    if datapack.lexer.do_while_box is None:
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected (", command[0], tokenizer, col_length=True)
        if command[1].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                "Expected (", command[1], tokenizer, display_col_length=False)
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected {", command[1], tokenizer, col_length=True)
        if command[1].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, display_col_length=False)

        condition, precommand = parse_condition(command[1], tokenizer)
        count = datapack.get_count(NAME)
        call_func = f"{precommand}execute {condition} run function {datapack.namespace}:{DataPack.PRIVATE_NAME}/{NAME}/{count}"
        datapack.add_custom_private_function(
            NAME, command[2], tokenizer, count, postcommands=[call_func])
        return call_func
    else:
        func_content = datapack.lexer.do_while_box
        datapack.lexer.do_while_box = None
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected (", command[0], tokenizer, col_length=True)
        if command[1].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                "Expected (", command[1], tokenizer, display_col_length=False)
        if len(command) > 2:
            raise JMCSyntaxException(
                f"Unexpected token", command[2], tokenizer, display_col_length=False)

        condition, precommand = parse_condition(command[1], tokenizer)
        count = datapack.get_count(NAME)
        call_func = datapack.add_custom_private_function(
            NAME, func_content, tokenizer, count, postcommands=[f"{precommand}execute {condition} run function {datapack.namespace}:{DataPack.PRIVATE_NAME}/{NAME}/{count}"])

        return call_func


def do(command: list[Token], datapack: DataPack, tokenizer: Tokenizer) -> None:
    if len(command) < 2:
        raise JMCSyntaxException(
            "Expected {", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.paren_curly:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, display_col_length=False)

    datapack.lexer.do_while_box = command[1]


SWITCH_CASE_NAME = 'switch_case'


def __parse_switch_binary(min_: int, max_: int, count: int, datapack: DataPack, func_contents: list[list[str]], scoreboard_player: ScoreboardPlayer) -> None:
    if max_ < min_:
        raise ValueError("min_ is less than max_ in __parse_switch_binary")
    if max_ == min_:
        datapack.add_raw_private_function(
            SWITCH_CASE_NAME, func_contents[min_-1], count)
    else:
        count_less = datapack.get_count(SWITCH_CASE_NAME)
        count_more = datapack.get_count(SWITCH_CASE_NAME)

        half2 = min_+(max_-min_+1)//2
        half1 = half2-1

        match_less = f"{min_}..{half1}" if min_ != half1 else min_
        match_more = f"{half2}..{max_}" if half2 != max_ else max_

        datapack.add_raw_private_function(
            SWITCH_CASE_NAME, [
                f"execute if score {scoreboard_player.value[1]} {scoreboard_player.value[0]} matches {match_less} run function {datapack.namespace}:{DataPack.PRIVATE_NAME}/{SWITCH_CASE_NAME}/{count_less}",
                f"execute if score {scoreboard_player.value[1]} {scoreboard_player.value[0]} matches {match_more} run function {datapack.namespace}:{DataPack.PRIVATE_NAME}/{SWITCH_CASE_NAME}/{count_more}",
            ], count)

        __parse_switch_binary(min_, half1, count_less,
                              datapack, func_contents, scoreboard_player)
        __parse_switch_binary(half2, max_, count_more,
                              datapack, func_contents, scoreboard_player)


def parse_switch(scoreboard_player: ScoreboardPlayer, func_contents: list[list[str]], datapack: DataPack) -> list[Token]:
    count = datapack.get_count(SWITCH_CASE_NAME)
    __parse_switch_binary(1, len(func_contents), count,
                          datapack, func_contents, scoreboard_player)
    return f"function {datapack.namespace}:{DataPack.PRIVATE_NAME}/{SWITCH_CASE_NAME}/{count}"


def switch(command: list[Token], datapack: DataPack, tokenizer: Tokenizer) -> str:
    if len(command) == 1:
        raise JMCSyntaxException(
            "Expected (", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.paren_round:
        raise JMCSyntaxException(
            "Expected (", command[1], tokenizer, display_col_length=False)
    if len(command) == 2:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, col_length=True)
    if command[2].token_type != TokenType.paren_curly:
        raise JMCSyntaxException(
            "Expected {", command[2], tokenizer, display_col_length=False)
    if command[2].string == '{}':
        raise JMCSyntaxException(
            "Switch content cannot be empty", command[2], tokenizer)

    list_of_tokens = tokenizer.parse(
        command[2].string[1:-1], command[2].line, command[2].col, expect_semicolon=True)

    case_count = 1
    cases_content: list[list[list[Token]]] = []
    current_case_content: list[list[Token]] = []
    if list_of_tokens[0][0].string != 'case' or list_of_tokens[0][0].token_type != TokenType.keyword:
        raise JMCSyntaxException(
            "Expected 'case'", list_of_tokens[0][0], tokenizer)

    for tokens in list_of_tokens:
        if tokens[0].string == 'case' and tokens[0].token_type == TokenType.keyword:
            cases_content.append(current_case_content)
            current_case_content = []
            if len(tokens) == 1:
                raise JMCSyntaxException(
                    "Expected case number", tokens[0], tokenizer, col_length=True)

            if tokens[1].string.endswith(":"):
                count_str = tokens[1].string[:-1]
                if not count_str.isalnum():
                    raise JMCSyntaxException(
                        "Expected case number", tokens[1], tokenizer)

                count = int(count_str)
                if count != case_count:
                    raise JMCSyntaxException(
                        f"Expected case {case_count} got case {count}", tokens[1], tokenizer)

                tokens = tokens[2:]
            else:
                count_str = tokens[1].string
                if not count_str.isalnum():
                    raise JMCSyntaxException(
                        "Expected case number", tokens[1], tokenizer)

                count = int(count_str)
                if count != case_count:
                    raise JMCSyntaxException(
                        f"Expected case {case_count} got case {count}", tokens[1], tokenizer)
                if len(tokens < 3):
                    raise JMCSyntaxException(
                        "Expected colon (:)", tokens[1], tokenizer, col_length=True)
                if tokens[2].token_type != TokenType.keyword or tokens[2].string != ':':
                    raise JMCSyntaxException(
                        "Expected colon (:)", tokens[2], tokenizer)

                tokens = tokens[3:]
            case_count += 1
        # End If case
        if tokens[0].string == 'break' and tokens[0].token_type == TokenType.keyword and len(tokens) == 1:
            continue
        current_case_content.append(tokens)

    cases_content.append(current_case_content)
    cases_content = cases_content[1:]

    func_contents: list[list[str]] = []
    for case_content in cases_content:
        func_contents.append(datapack.lexer._parse_func_content(
            tokenizer, case_content, is_load=False))

    # Parse variable
    tokens = tokenizer.parse(
        command[1].string[1:-1], command[1].line, command[1].col, expect_semicolon=False)[0]
    if len(tokens) > 1:
        raise JMCSyntaxException(
            f"Unexpected token({tokens[1].string})", tokens[1], tokenizer)

    scoreboard_player = find_scoreboard_player_type(tokens[0], tokenizer)
    if scoreboard_player.player_type == PlayerType.integer:
        raise JMCSyntaxException(
            f"Unexpected integer in switch case", tokens[0], tokenizer)

    return parse_switch(scoreboard_player, func_contents, datapack)


def for_(command: list[Token], datapack: DataPack, tokenizer: Tokenizer) -> str:
    return "for_"+str(command)
