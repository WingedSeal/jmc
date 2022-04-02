from ..exception import JMCSyntaxException, JMCTypeError
from ..tokenizer import Token, TokenType, Tokenizer
from ..datapack import DataPack
from .utils import ArgType, eval_expr, find_scoreboard_player_type, verify_args
from ._flow_control import parse_switch

HARDCODE_REPEAT_ARG_TYPE = {
    "index_string": ArgType.string,
    "function": ArgType.arrow_func,
    "count": ArgType.integer,
    "start": ArgType.integer,
    "stop": ArgType.integer,
    "step": ArgType.integer
}


def hardcode_repeat(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(HARDCODE_REPEAT_ARG_TYPE,
                       "Hardcode.repeat", token, tokenizer)

    if args["index_string"] is None:
        raise JMCTypeError("index_string", token, tokenizer)
    else:
        index_string = args["index_string"].token.string

    if args["function"] is None:
        raise JMCTypeError("function", token, tokenizer)

    if args["start"] is None:
        start = 0
    else:
        start = int(args["start"].token.string)

    if args["stop"] is None:
        raise JMCTypeError("stop", token, tokenizer)
    else:
        stop = int(args["stop"].token.string)

    if args["step"] is None:
        step = 1
    else:
        step = int(args["step"].token.string)
        if step == 0:
            raise JMCSyntaxException(
                "'step' must not be zero", args["step"].token, tokenizer)

    commands: list[str] = []
    for i in range(start, stop, step):
        try:
            commands.extend(datapack.parse_function_token(
                Token(
                    TokenType.paren_curly,
                    args["function"].token.line,
                    args["function"].token.col,
                    __hardcode_process(
                        args["function"].token.string, index_string, i, token, tokenizer
                    )
                ), tokenizer)
            )
        except JMCSyntaxException as error:
            error.msg = 'WARNING: This error happens inside Hardcode.repeat, if you use Hardcode.calc the error position might not be accurate\n\n' + error.msg
            raise error

    return "\n".join(commands)


HARDCODE_SWITCH_ARG_TYPE = {
    "switch": ArgType.scoreboard,
    "index_string": ArgType.string,
    "function": ArgType.arrow_func,
    "count": ArgType.integer
}


def hardcode_switch(token: Token, datapack: DataPack, tokenizer: Tokenizer) -> str:
    args = verify_args(HARDCODE_SWITCH_ARG_TYPE,
                       "Hardcode.switch", token, tokenizer)

    if args["switch"] is None:
        raise JMCTypeError("switch", token, tokenizer)
    else:
        scoreboard_player = find_scoreboard_player_type(
            args["switch"].token, tokenizer)

    if args["index_string"] is None:
        raise JMCTypeError("index_string", token, tokenizer)
    else:
        index_string = args["index_string"].token.string

    if args["function"] is None:
        raise JMCTypeError("function", token, tokenizer)

    if args["count"] is None:
        raise JMCTypeError("count", token, tokenizer)
    else:
        count = int(args["count"].token.string)

    func_contents: list[list[str]] = []
    for i in range(count):
        try:
            func_contents.append(datapack.parse_function_token(
                Token(
                    TokenType.paren_curly,
                    args["function"].token.line,
                    args["function"].token.col,
                    __hardcode_process(
                        args["function"].token.string, index_string, i, token, tokenizer
                    )
                ), tokenizer)
            )
        except JMCSyntaxException as error:
            error.msg = 'WARNING: This error happens inside Hardcode.switch, if you use Hardcode.calc the error position might not be accurate\n\n' + error.msg
            raise error

    return parse_switch(scoreboard_player, func_contents, datapack, name="hardcode_switch")


def __hardcode_parse(calc_pos: int, string: str, token: Token, tokenizer: Tokenizer) -> str:
    count = 0
    expression = ''
    index = calc_pos
    if len(string) < calc_pos+14 or string[calc_pos+13] != '(':
        raise JMCSyntaxException(
            f"Expected ( after Hardcode.calc", token, tokenizer, display_col_length=False)
    for char in string[calc_pos+13:]:  # len('Hardcode.calc') = 13
        index += 1
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1

        if char not in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', '*', '/', ' ', '\t', '\n', '(', ')'}:
            raise JMCSyntaxException(
                f"Invalid charater({char}) in Hardcode.calc", token, tokenizer, display_col_length=False)

        expression += char
        if count == 0:
            break

    if count != 0:
        raise JMCSyntaxException(
            f"Invalid syntax in Hardcode.calc", token, tokenizer, display_col_length=False)

    return string[:calc_pos]+eval_expr(expression)+string[index+13:]


def __hardcode_process(string: str, index_string: str, i: int, token: Token, tokenizer: Tokenizer) -> str:
    string = string.replace(index_string, str(i))
    calc_pos = string.find('Hardcode.calc')
    if calc_pos != -1:
        string = __hardcode_parse(calc_pos, string, token, tokenizer)
    return string
