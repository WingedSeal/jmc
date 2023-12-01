"""Module for parsing flow controls (if-e;se, while, etc.), called from command/flow_control.py"""

from typing import Literal
from .condition import parse_condition
from .utils import ScoreboardPlayer, find_scoreboard_player_type, merge_obj_selector, is_obj_selector, PlayerType
from ..tokenizer import Token, Tokenizer, TokenType
from ..datapack import DataPack
from ..exception import JMCSyntaxException


def if_(command: list[Token], datapack: DataPack,
        tokenizer: Tokenizer, prefix: str) -> str | None:
    """
    Parse `if`
    """
    if len(command) < 2:
        raise JMCSyntaxException(
            "Expected (", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.PAREN_ROUND:
        raise JMCSyntaxException(
            "Expected (", command[1], tokenizer, display_col_length=False)
    if len(command) < 3:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, col_length=True)
    if command[2].string == "expand":
        if len(command) < 4:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, col_length=True)
        datapack.lexer.if_else_box.append((command[1], command[3]))
        return datapack.lexer.parse_if_else(tokenizer, prefix, is_expand=True)

    if command[2].token_type != TokenType.PAREN_CURLY:
        datapack.lexer.if_else_box.append((command[1], command[2:]))
        return None

    datapack.lexer.if_else_box.append((command[1], command[2]))
    return None


def macro_if(command: list[Token], datapack: DataPack,
             tokenizer: Tokenizer, prefix: str) -> str | None:
    if len(command) < 2:
        raise JMCSyntaxException(
            "Expected (", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.PAREN_ROUND:
        raise JMCSyntaxException(
            "Expected (", command[1], tokenizer, display_col_length=False)
    if len(command) < 3:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, col_length=True)
    if command[2].string == "expand":
        if len(command) < 4:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, col_length=True)
        datapack.lexer.if_else_box.append((command[1], command[3]))
        return datapack.lexer.parse_if_else(
            tokenizer, prefix, is_expand=True, is_macro=True)

    if command[2].token_type != TokenType.PAREN_CURLY:
        datapack.lexer.if_else_box.append((command[1], command[2:]))
        return datapack.lexer.parse_if_else(tokenizer, prefix, is_macro=True)

    datapack.lexer.if_else_box.append((command[1], command[2]))
    return datapack.lexer.parse_if_else(tokenizer, prefix, is_macro=True)


def else_(command: list[Token], datapack: DataPack,
          tokenizer: Tokenizer, prefix: str) -> str | None:
    """
    Parse `else`
    """
    if not datapack.lexer.if_else_box:
        raise JMCSyntaxException(
            "'else' cannot be used without 'if'", command[0], tokenizer)

    if len(command) < 2:
        raise JMCSyntaxException(
            "Expected 'if' or {", command[0], tokenizer, col_length=True)

    if command[1].token_type == TokenType.KEYWORD and command[1].string == "if":
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected (", command[1], tokenizer, col_length=True)
        if command[2].token_type != TokenType.PAREN_ROUND:
            raise JMCSyntaxException(
                "Expected (", command[2], tokenizer, display_col_length=False)
        if len(command) < 4:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, col_length=True)
        if command[3].token_type != TokenType.PAREN_CURLY:
            # raise JMCSyntaxException(
            #     "Expected {", command[3], tokenizer, display_col_length=False)
            datapack.lexer.if_else_box.append(
                (command[2], command[3:]))
            return None

        datapack.lexer.if_else_box.append(
            (command[2], command[3]))
        return None
    if command[1].token_type == TokenType.PAREN_CURLY:
        datapack.lexer.if_else_box.append(
            (None, command[1])
        )
    else:
        datapack.lexer.if_else_box.append(
            (None, command[1:])
        )
    return datapack.lexer.parse_if_else(tokenizer, prefix)

    # raise JMCSyntaxException(
    #     "Expected 'if' or {", command[1], tokenizer, display_col_length=False)


WHILE_NAME = "while_loop"


def while_(command: list[Token], datapack: "DataPack",
           tokenizer: "Tokenizer", prefix: str) -> str:
    """
    Parse `while`
    """
    if datapack.lexer.do_while_box is None:
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected (", command[0], tokenizer, col_length=True)
        if command[1].token_type != TokenType.PAREN_ROUND:
            raise JMCSyntaxException(
                "Expected (", command[1], tokenizer, display_col_length=False)
        if len(command) < 3:
            raise JMCSyntaxException(
                "Expected {", command[1], tokenizer, col_length=True)
        if command[1].token_type != TokenType.PAREN_ROUND:
            raise JMCSyntaxException(
                "Expected {", command[2], tokenizer, display_col_length=False)

        condition, precommand = parse_condition(
            command[1], tokenizer, datapack)
        count = datapack.get_count(WHILE_NAME)
        call_func = f"{precommand}execute {condition} run function {datapack.namespace}:{DataPack.private_name}/{WHILE_NAME}/{count}"
        datapack.add_custom_private_function(
            WHILE_NAME, command[2], tokenizer, count, prefix, postcommands=[call_func])
        return call_func

    else:
        func_content = datapack.lexer.do_while_box
        datapack.lexer.do_while_box = None
        if len(command) < 2:
            raise JMCSyntaxException(
                "Expected (", command[0], tokenizer, col_length=True)
        if command[1].token_type != TokenType.PAREN_ROUND:
            raise JMCSyntaxException(
                "Expected (", command[1], tokenizer, display_col_length=False)
        if len(command) > 2:
            raise JMCSyntaxException(
                "Unexpected token", command[2], tokenizer, display_col_length=False)

        condition, precommand = parse_condition(
            command[1], tokenizer, datapack)
        count = datapack.get_count(WHILE_NAME)
        call_func = datapack.add_custom_private_function(
            WHILE_NAME, func_content, tokenizer, count, prefix, postcommands=[f"{precommand}execute {condition} run function {datapack.namespace}:{DataPack.private_name}/{WHILE_NAME}/{count}"])

        return call_func


def do(command: list[Token], datapack: DataPack,
       tokenizer: Tokenizer, prefix: str) -> None:
    """
    Parse `do`
    """
    if len(command) < 2:
        raise JMCSyntaxException(
            "Expected {", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.PAREN_CURLY:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, display_col_length=False)

    datapack.lexer.do_while_box = command[1]


SWITCH_CASE_NAME = "switch_case"


def __parse_switch_binary(min_: int, max_: int, count: str, datapack: DataPack,
                          func_contents: list[list[str]], scoreboard_player: ScoreboardPlayer, name: str, start_at: int = 1) -> None:
    """
    For recursion of JMC switch-case's binary tree

    :param min_: Minimum integer to trigger minecraft function
    :param max_: Maximum integer to trigger minecraft function
    :param count: Private function count for creating name of private function
    :param datapack: Datapack object
    :param func_contents: List of function content(List of commands(string)) given by user
    :param scoreboard_player: Minecraft scoreboard objective to check the integer
    :param name: Private function's group name
    :raises ValueError: min_ is more than max_
    """
    if max_ < min_:
        raise ValueError("min_ is more than max_ in __parse_switch_binary")
    if max_ == min_:
        datapack.add_raw_private_function(
            name, func_contents[min_ - start_at], count)
    else:
        count_less = datapack.get_count(name)
        count_more = datapack.get_count(name)

        half2 = min_ + (max_ - min_ + 1) // 2
        half1 = half2 - 1

        match_less = f"{min_}..{half1}" if min_ != half1 else min_
        match_more = f"{half2}..{max_}" if half2 != max_ else max_

        if isinstance(scoreboard_player.value, int):
            raise ValueError("scoreboard_player.value is int")

        datapack.add_raw_private_function(
            name, [
                f"execute if score {scoreboard_player.value[1]} {scoreboard_player.value[0]} matches {match_less} run function {datapack.namespace}:{DataPack.private_name}/{name}/{count_less}",
                f"execute if score {scoreboard_player.value[1]} {scoreboard_player.value[0]} matches {match_more} run function {datapack.namespace}:{DataPack.private_name}/{name}/{count_more}",
            ], count)

        __parse_switch_binary(min_, half1, count_less,
                              datapack, func_contents, scoreboard_player, name, start_at)
        __parse_switch_binary(half2, max_, count_more,
                              datapack, func_contents, scoreboard_player, name, start_at)


def parse_switch(scoreboard_player: ScoreboardPlayer,
                 func_contents: list[list[str]], datapack: DataPack, name: str = SWITCH_CASE_NAME, start_at: int = 1, case_numbers: list[int | Literal["default"]] | None = None) -> str:
    """
    Create a binary tree for JMC switch-case

    :param scoreboard_player: Minecraft scoreboard objective to check the integer
    :param func_contents: List of function content(List of commands(string)) given by user
    :param datapack: Datapack object
    :param name: Private function's group name, defaults to SWITCH_CASE_NAME
    :param case_numbers: List of case numbers provided (only matters with post-1.20.2 switch)
    :return: Minecraft function call to initiate switch case
    """
    assert not isinstance(scoreboard_player.value, int)
    if case_numbers is None:
        case_numbers = [*range(1, len(func_contents) + 1)]
    func_count = datapack.get_count(name)
    if datapack.version >= 16:
        has_default = "default" in case_numbers
        for (case_body, case_label) in zip(func_contents, case_numbers):
            if has_default and case_label != "default":
                case_body.append(
                    f"scoreboard players set __found_case__ {datapack.var_name} 1")
            datapack.add_raw_private_function(
                name, case_body, f"{str(func_count)}/{case_label}")
        datapack.add_raw_private_function(
            name, [
                f"$function {datapack.namespace}:{DataPack.private_name}/{name}/{func_count}/$(switch_key)"
            ], f"{str(func_count)}/select")
        return (
            (f"scoreboard players set __found_case__ {datapack.var_name} 0\n" if has_default else "") +
            f"execute store result storage {datapack.namespace}:{datapack.storage_name} switch_key int 1 run scoreboard players get {scoreboard_player.value[1]} {scoreboard_player.value[0]}" +
            f"\nfunction {datapack.namespace}:{DataPack.private_name}/{name}/{func_count}/select with storage {datapack.namespace}:{datapack.storage_name}" +
            (f"\nexecute unless score __found_case__ {datapack.var_name} matches 1 run function {datapack.namespace}:{DataPack.private_name}/{name}/{func_count}/default" if has_default else "")
        )

    switch_id = datapack.data.get_current_switch()
    temp_score = ScoreboardPlayer(player_type=PlayerType.SCOREBOARD,
                                  value=(datapack.var_name, switch_id))
    __parse_switch_binary(
        start_at,
        len(func_contents) +
        start_at -
        1,
        func_count,
        datapack,
        func_contents,
        temp_score,
        name,
        start_at)
    return (f"scoreboard players operation {switch_id} {datapack.var_name} = {scoreboard_player.value[1]} {scoreboard_player.value[0]}\n" +
            f"function {datapack.namespace}:{DataPack.private_name}/{name}/{func_count}")


def switch(command: list[Token], datapack: DataPack,
           tokenizer: Tokenizer, prefix: str) -> str:
    """
    Parse `switch`
    """
    if len(command) == 1:
        raise JMCSyntaxException(
            "Expected (", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.PAREN_ROUND:
        raise JMCSyntaxException(
            "Expected (", command[1], tokenizer, display_col_length=False)
    if len(command) == 2:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, col_length=True)
    if command[2].token_type != TokenType.PAREN_CURLY:
        raise JMCSyntaxException(
            "Expected {", command[2], tokenizer, display_col_length=False)
    if command[2].string == "{}":
        raise JMCSyntaxException(
            "Switch content cannot be empty", command[2], tokenizer)

    list_of_tokens = tokenizer.parse(
        command[2].string[1:-1], command[2].line, command[2].col + 1, expect_semicolon=True)

    case_numbers: list[int | Literal["default"]] = []
    expected_case: int | None = None
    case_start: int | None = None
    cases_content: list[list[list[Token]]] = []
    current_case_content: list[list[Token]] = []
    if list_of_tokens[0][0].string != "case" or list_of_tokens[0][0].token_type != TokenType.KEYWORD:
        raise JMCSyntaxException(
            "Expected 'case'", list_of_tokens[0][0], tokenizer)

    for tokens in list_of_tokens:
        if tokens[0].string == "case" and tokens[0].token_type == TokenType.KEYWORD:
            cases_content.append(current_case_content)
            current_case_content = []
            if len(tokens) == 1:
                raise JMCSyntaxException(
                    "Expected case number", tokens[0], tokenizer, col_length=True)
            if tokens[1].string == "-":
                count_str = tokens[1].string + tokens[2].string
                del tokens[2]
            else:
                count_str = tokens[1].string
            if not count_str.lstrip("-").isalnum():
                raise JMCSyntaxException(
                    "Expected case number", tokens[1], tokenizer)

            count = int(count_str)
            if expected_case is None:
                expected_case = count
            if case_start is None:
                case_start = expected_case
            if count != expected_case:
                datapack.version.require(
                    16, tokens[1], tokenizer, suggestion=f"Expected case number {expected_case}")
            if len(tokens) < 3:
                raise JMCSyntaxException(
                    "Expected colon (:)", tokens[1], tokenizer, col_length=True)
            if tokens[2].token_type != TokenType.OPERATOR or tokens[2].string != ":":
                raise JMCSyntaxException(
                    "Expected colon (:)", tokens[2], tokenizer)

            tokens = tokens[3:]
            expected_case += 1
            case_numbers.append(count)
        if tokens[0].string == "default" and tokens[0].token_type == TokenType.KEYWORD:
            datapack.version.require(16, tokens[1], tokenizer)
            cases_content.append(current_case_content)
            current_case_content = []
            case_numbers.append("default")
            tokens = tokens[2:]
        # End If case
        if tokens[0].string == "break" and tokens[0].token_type == TokenType.KEYWORD and len(
                tokens) == 1:
            continue
        current_case_content.append(tokens)

    cases_content.append(current_case_content)
    cases_content = cases_content[1:]

    func_contents: list[list[str]] = []
    for case_content in cases_content:
        func_contents.append(datapack.lexer._parse_func_content(
            tokenizer, case_content, prefix, is_load=False))

    # Parse variable
    tokens = tokenizer.parse(
        command[1].string[1:-1], command[1].line, command[1].col + 1, expect_semicolon=False)[0]

    if len(tokens) > 1:
        if is_obj_selector(tokens):
            tokens = [merge_obj_selector(tokens, tokenizer, datapack)]
        else:
            raise JMCSyntaxException(
                f"Unexpected token({tokens[1].string})", tokens[1], tokenizer)

    scoreboard_player = find_scoreboard_player_type(
        tokens[0], tokenizer, allow_integer=False)

    if scoreboard_player.player_type == PlayerType.INTEGER:
        raise JMCSyntaxException(
            "Unexpected integer in switch case", tokens[0], tokenizer)

    if case_start is None:
        raise ValueError("case_start is None")

    return parse_switch(scoreboard_player, func_contents,
                        datapack, start_at=case_start, case_numbers=case_numbers)


FOR_NAME = "for_loop"


def for_(command: list[Token], datapack: DataPack,
         tokenizer: Tokenizer, prefix: str) -> str:
    """
    Parse `for`
    """
    if len(command) == 1:
        raise JMCSyntaxException(
            "Expected (", command[0], tokenizer, col_length=True)
    if command[1].token_type != TokenType.PAREN_ROUND:
        raise JMCSyntaxException(
            "Expected (", command[1], tokenizer, display_col_length=False)
    if len(command) == 2:
        raise JMCSyntaxException(
            "Expected {", command[1], tokenizer, col_length=True)
    if command[2].token_type != TokenType.PAREN_CURLY:
        raise JMCSyntaxException(
            "Expected {", command[2], tokenizer, display_col_length=False)
    if command[2].string == "{}":
        raise JMCSyntaxException(
            "For loop content cannot be empty", command[2], tokenizer)
    statements = tokenizer.parse(command[1].string[1:-1], command[1].line,
                                 command[1].col + 1, expect_semicolon=True, allow_last_missing_semicolon=True)
    if len(statements) != 3:
        raise JMCSyntaxException(
            f"Expected 3 statements (got {len(statements)})", command[1], tokenizer)

    if statements[0][0].string in {
            "let", "var"} and statements[0][0].token_type == TokenType.KEYWORD:
        raise JMCSyntaxException(
            f"JMC does not support local scope variable, do not use '{statements[0][0].string}' keyword", statements[0][0], tokenizer)

    _first_statement = statements[0]
    # if not (_first_statement[0].string.startswith(
    #         DataPack.VARIABLE_SIGN) and _first_statement[0].token_type == TokenType.KEYWORD):
    #     raise JMCSyntaxException(
    #         "First statement in for loop must be variable assignment", _first_statement[0], tokenizer, suggestion="Please use $<variable> = <integer|$variable>|<objective>:<selector>")

    first_statement = datapack.lexer.parse_line(
        _first_statement, tokenizer, prefix)

    # if not (_first_statement[1].string ==
    #         "=" and _first_statement[1].token_type == TokenType.OPERATOR):
    #     raise JMCSyntaxException(
    #         "First statement in for loop must be variable assignment", _first_statement[0], tokenizer, suggestion=f"{_first_statement[1].string} operator is not supported")

    condition, precommand = parse_condition(statements[1], tokenizer, datapack)
    last_statement = datapack.lexer.parse_line(
        statements[2], tokenizer, prefix)

    count = datapack.get_count(FOR_NAME)
    call_func = f"{precommand}execute {condition} run {datapack.call_func(FOR_NAME, count)}"

    datapack.add_custom_private_function(
        FOR_NAME,
        command[2],
        tokenizer,
        count,
        prefix,
        postcommands=[
            *last_statement,
            call_func
        ]
    )

    return "\n".join([
        *first_statement,
        call_func
    ])
