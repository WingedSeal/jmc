"""Module containing JMCFunction subclasses for custom JMC function thatcannot be used with `/execute`"""

from ...tokenizer import Token, Tokenizer, TokenType
from ...exception import JMCSyntaxException
from ..jmc_function import JMCFunction, FuncType, func_property
from ..utils import ArgType, eval_expr, find_scoreboard_player_type
from .._flow_control import parse_switch


def _hardcode_parse(calc_pos: int, string: str, token: Token, tokenizer: Tokenizer) -> str:
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


def _hardcode_process(string: str, index_string: str, i: int, token: Token, tokenizer: Tokenizer) -> str:
    string = string.replace(index_string, str(i))
    calc_pos = string.find('Hardcode.calc')
    if calc_pos != -1:
        string = _hardcode_parse(calc_pos, string, token, tokenizer)
    return string


@func_property(
    func_type=FuncType.execute_excluded,
    call_string='Hardcode.repeat',
    arg_type={
        "index_string": ArgType.string,
        "function": ArgType.arrow_func,
        "start": ArgType.integer,
        "stop": ArgType.integer,
        "step": ArgType.integer
    },
    name='hardcode_repeat',
    ignore={
        "function"
    },
    defaults={
        "start": "0",
        "step": "1"
    }
)
class HardcodeRepeat(JMCFunction):
    def call(self) -> str:
        start = int(self.args["start"])
        step = int(self.args["step"])
        stop = int(self.args["stop"])
        if step == 0:
            raise JMCSyntaxException(
                "'step' must not be zero", self.args_Args["step"].token, self.tokenizer)

        commands: list[str] = []
        for i in range(start, stop, step):
            try:
                commands.extend(self.datapack.parse_function_token(
                    Token(
                        TokenType.paren_curly,
                        self.args_Args["function"].token.line,
                        self.args_Args["function"].token.col,
                        _hardcode_process(
                            self.args_Args["function"].token.string, self.args["index_string"], i, self.token, self.tokenizer
                        )
                    ), self.tokenizer)
                )
            except JMCSyntaxException as error:
                error.msg = 'WARNING: This error happens inside Hardcode.repeat, if you use Hardcode.calc the error position might not be accurate\n\n' + error.msg
                raise error

        return "\n".join(commands)


@func_property(
    func_type=FuncType.execute_excluded,
    call_string='Hardcode.switch',
    arg_type={
        "switch": ArgType.scoreboard,
        "index_string": ArgType.string,
        "function": ArgType.arrow_func,
        "count": ArgType.integer
    },
    name='hard_code_switch',
    ignore={
        "function",
        "switch"
    },
)
class HardcodeSwitch(JMCFunction):
    def call(self) -> str:
        count = int(self.args["count"])
        func_contents: list[list[str]] = []
        scoreboard_player = find_scoreboard_player_type(
            self.args_Args["switch"].token, self.tokenizer)
        for i in range(count):
            try:
                func_contents.append(self.datapack.parse_function_token(
                    Token(
                        TokenType.paren_curly,
                        self.args_Args["function"].token.line,
                        self.args_Args["function"].token.col,
                        _hardcode_process(
                            self.args_Args["function"].token.string, self.args["index_string"], i, self.token, self.tokenizer
                        )
                    ), self.tokenizer)
                )
            except JMCSyntaxException as error:
                error.msg = 'WARNING: This error happens inside Hardcode.switch, if you use Hardcode.calc the error position might not be accurate\n\n' + error.msg
                raise error

        return parse_switch(scoreboard_player, func_contents, self.datapack, self.name)
