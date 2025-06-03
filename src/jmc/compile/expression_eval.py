from dataclasses import dataclass
import bisect
from typing import Any, cast
from enum import Enum, auto
from math import log2

from jmc.compile.utils import is_float

from .command.condition import FUNC_CONTENT

from .exception import JMCSyntaxException
from .datapack import DataPack

from .command.utils import eval_expr, is_number
from .tokenizer import Token, TokenType, Tokenizer


OPERATOR_STRINGS = list("+-*/%") + ["**"]


class CustomOrder:
    def __init__(self, order: int, line: int, col: int, is_left_precedence: bool = True) -> None:
        self.order = order
        self.line = line
        self.col = col
        self.is_left_precedence = is_left_precedence

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, CustomOrder):
            raise ValueError("CustomOrder is compared against other class")
        if self.order != other.order:
            return self.order < other.order
        if self.line != other.line:
            if self.is_left_precedence:
                return self.line > other.line
            else:
                return self.line < other.line
        if self.is_left_precedence:
            return self.col > other.col
        else:
            return self.col < other.col


class OpenBracket:
    def get_order(self) -> CustomOrder:
        return CustomOrder(0, 0, 0)


OPEN_BRACKET = OpenBracket()


@dataclass
class Node:
    content: str
    token: Token


@dataclass
class Operator(Node):
    def get_order(self) -> CustomOrder:
        if self.content == "**":
            return CustomOrder(30, self.token.line, self.token.col, is_left_precedence=False)
        elif self.content in "*/%":
            return CustomOrder(20, self.token.line, self.token.col)
        elif self.content in "+-":
            return CustomOrder(10, self.token.line, self.token.col)
        else:
            raise ValueError(f"{self.content} is not a known operator")

    def is_reflective(self) -> bool:
        if self.content in "+*":
            return True
        elif self.content in "-/%" or self.content == "**":
            return False
        else:
            raise ValueError(f"{self.content} is not a known operator")

    def is_same_group(self, other: "Operator") -> bool:
        if self.content == other.content:
            return True
        if self.content in "+-" and other.content in "+-":
            return True
        return False


@dataclass
class Number(Node):
    pass


@dataclass
class CommandNumber(Number):
    pass


@dataclass
class Constant(Number):
    pass


@dataclass
class Variable(Number):
    pass


@dataclass
class TemporaryVariable(Variable):
    index: int


@dataclass
class Expression(Number):
    children: tuple[Number, Number]
    operator: Operator

    def __post_init__(self):
        if self.operator.is_reflective() and not isinstance(self.children[0], Expression) and isinstance(self.children[1], Expression):
            self.children = (self.children[1], self.children[0])


def tokens_to_tokens(tokens: list[Token], tokenizer: Tokenizer) -> list[Token]:
    return_tokens: list[Token] = []
    is_hanging_negative_sign = False
    for token in tokens:
        if token.token_type == TokenType.OPERATOR:
            if token.string == ":":
                if not return_tokens:
                    raise JMCSyntaxException(
                        "Unexpected ':' in expression evaluation", token, tokenizer)
                return_tokens[-1] = tokenizer.merge_tokens(
                    [return_tokens[-1], token])
            elif token.string == "::":
                raise JMCSyntaxException(
                    "NBT operation is not directly supported by expression evaluation",
                    token,
                    tokenizer,
                    suggestion="Use command expression '{}' instead. Change '::path' to '{::path}'")
            else:
                if token.string == "-" and (not return_tokens or (return_tokens[-1].token_type == TokenType.OPERATOR and return_tokens[-1].string != ")")):
                    is_hanging_negative_sign = True
                return_tokens.append(token)
                continue
        elif token.token_type == TokenType.PAREN_ROUND:
            tokenizer_ = Tokenizer(
                token.string[1:-1],
                tokenizer.file_path,
                token.line,
                token.col + 1,
                tokenizer.file_string,
                expect_semicolon=False,
                allow_semicolon=False
            )
            if is_hanging_negative_sign:
                negative_sign_token = return_tokens.pop()
                return_tokens.append(
                    Token(TokenType.KEYWORD, negative_sign_token.line, negative_sign_token.col, "-1"))
                return_tokens.append(Token(TokenType.OPERATOR,
                                           negative_sign_token.line, negative_sign_token.col, "*"))
                is_hanging_negative_sign = False

            return_tokens.append(Token(TokenType.OPERATOR,
                                       token.line, token.col, "("))
            return_tokens.extend(tokens_to_tokens(
                tokenizer_.programs[0], tokenizer))
            return_tokens.append(Token(TokenType.OPERATOR, token.line +
                                       token.string.count("\n"), token.col + token.length, ")"))
        elif token.token_type == TokenType.PAREN_CURLY:
            return_tokens.append(token)
        elif token.token_type == TokenType.PAREN_SQUARE:
            if return_tokens and return_tokens[-1] and ":" in return_tokens[-1].string:
                return_tokens[-1] = tokenizer.merge_tokens(
                    [return_tokens[-1], token])
            else:
                raise JMCSyntaxException(
                    f"Unexpected {token.token_type.value} token in expression", token, tokenizer)
        elif token.token_type == TokenType.KEYWORD:
            if return_tokens and return_tokens[-1].token_type == TokenType.KEYWORD:
                return_tokens[-1] = tokenizer.merge_tokens(
                    [return_tokens[-1], token])
            elif is_hanging_negative_sign:
                is_hanging_negative_sign = False
                if is_number(token.string):
                    return_tokens[-1] = tokenizer.merge_tokens(
                        [return_tokens[-1], token])
                elif token.token_type == TokenType.KEYWORD:
                    negative_sign_token = return_tokens.pop()
                    return_tokens.append(
                        Token(TokenType.KEYWORD, negative_sign_token.line, negative_sign_token.col, "-1"))
                    return_tokens.append(Token(TokenType.OPERATOR,
                                               negative_sign_token.line, negative_sign_token.col, "*"))
                    return_tokens.append(token)
                else:
                    raise JMCSyntaxException(
                        "Unexpected hanging negative sign (-) in an expression", return_tokens[-1], tokenizer)
            else:
                return_tokens.append(token)
        else:
            raise JMCSyntaxException(
                f"Unexpected {token.token_type.value} token in expression", token, tokenizer
            )
        if is_hanging_negative_sign:
            raise JMCSyntaxException(
                "Unexpected hanging negative sign (-) in an expression", return_tokens[-1], tokenizer)

    return return_tokens


def expression_to_tree(expression: list[Token], tokenizer: Tokenizer, datapack: "DataPack", prefix: str) -> Number:
    operator_stack: list[Operator | OpenBracket] = []
    number_stack: list[Number] = []

    def process_stack(is_consume_bracket: bool = False):
        while operator_stack:
            operator = operator_stack.pop()
            if isinstance(operator, OpenBracket):
                if not is_consume_bracket:
                    operator_stack.append(operator)
                break
            if len(number_stack) < 2:
                raise JMCSyntaxException(
                    "Number stack is empty when trying to evaluate the expression", operator.token, tokenizer)
            right = number_stack.pop()
            left = number_stack.pop()
            number_stack.append(Expression(
                operator.content, operator.token, (left, right), operator))

    for token in expression:
        if is_float(token.string):
            number_stack.append(Constant(token.string, token))
        elif token.string in OPERATOR_STRINGS:
            operator = Operator(token.string, token)
            if operator_stack and operator.get_order() < operator_stack[-1].get_order():
                process_stack()
            operator_stack.append(operator)
        elif token.token_type == TokenType.PAREN_CURLY:
            tokenizer_ = Tokenizer(
                token.string[1:-1],
                tokenizer.file_path,
                token.line,
                token.col + 1,
                tokenizer.file_string,
                expect_semicolon=False
            )
            func = FUNC_CONTENT[0](
                tokenizer_, tokenizer_.programs, is_load=False, lexer=datapack.lexer, prefix=prefix
            ).parse()
            if len(func) > 1:
                raise JMCSyntaxException(
                    "Command evaluation '{}' inside expression evaluation cannot return multiple command", token, tokenizer_)
            number_stack.append(CommandNumber(func[0], token))
        elif token.string == "(":
            operator_stack.append(OPEN_BRACKET)
        elif token.string == ")":
            process_stack(is_consume_bracket=True)
        elif token.string.startswith("$"):
            number_stack.append(
                Variable(f"{token.string} {DataPack.var_name}", token))
        elif ":" in token.string:
            objective, player = token.string.split(":")
            number_stack.append(
                Variable(f"{player} {objective}", token))
        else:
            raise JMCSyntaxException(
                "Unrecognized expression token", token, tokenizer)
    process_stack()
    if len(number_stack) > 1:
        raise JMCSyntaxException(
            "Number stack is not empty at the end of expression evaluation", number_stack[0].token, tokenizer)
    return number_stack[0]


def print_tree(node: Node, indent: str = "", is_left: bool = False) -> None:
    if isinstance(node, Expression):
        if len(node.children) > 1:
            print(
                f"{indent}{'├── ' if is_left else '└── '}{node.content}")
        elif len(node.children) > 0:
            print(
                f"{indent}{'├── ' if is_left else '└── '}{node.content}")
        else:
            print(f"{indent}{node.content}")
        if len(node.children) > 0:
            print_tree(node.children[0], indent +
                       ("│   " if is_left else "    "), True)
        if len(node.children) > 1:
            print_tree(node.children[1], indent +
                       ("│   " if is_left else "    "), False)
    else:
        print(f"{indent}{'├── ' if is_left else '└── '}{node.content}")


EXPONENTIAL_CAP = 5000


def tree_to_operations(tree: Number, output: Variable, tokenizer: Tokenizer) -> list[tuple[Variable, Operator, Number]]:
    if not isinstance(tree, Expression):
        return [(output, Operator("", Token.empty()), tree)]
    operations: list[tuple[Variable, Operator, Number]] = []
    max_index = 0
    free_temporary_variable: list[TemporaryVariable] = []
    all_temporary_variable: list[TemporaryVariable] = []
    output_variable: TemporaryVariable | None = None

    can_inject = search_for_output_in_tree(tree, output)

    def new_variable() -> TemporaryVariable:
        if free_temporary_variable:
            return free_temporary_variable.pop(0)
        nonlocal max_index
        max_index += 1
        temporary_variable = TemporaryVariable(
            "", Token.empty(), max_index)
        all_temporary_variable.append(temporary_variable)
        return temporary_variable

    def _tree_to_operation(node: Number, is_first_time: bool = True) -> Number:
        if isinstance(node, CommandNumber):
            new_var = new_variable()
            operations.append((new_var, Operator(
                "", Token.empty()), node))
            return new_var
        if not isinstance(node, Expression):
            return node
        nonlocal output_variable
        left_var = _tree_to_operation(node.children[0], False)
        right_var = _tree_to_operation(node.children[1], False)
        if isinstance(left_var, TemporaryVariable):
            if is_first_time:
                output_variable = left_var
            if isinstance(right_var, TemporaryVariable):
                bisect.insort(free_temporary_variable,
                              right_var, key=lambda x: x.index)
            if node.content == "**":
                if not isinstance(right_var, Constant):
                    raise JMCSyntaxException(
                        "Power operator (**) only works on a constant", right_var.token, tokenizer)
                times = float(right_var.content)
                if times < 0:
                    raise JMCSyntaxException(
                        "Power operator (**) only works on a positive number as there's no float in minecraft scoreboard", right_var.token, tokenizer)
                elif not times.is_integer():
                    raise JMCSyntaxException(
                        "Power operator (**) only works on a whole integer", right_var.token, tokenizer)
                elif times == 0:
                    operations.append(
                        (left_var, Operator("", Token.empty()), Constant("1", Token.empty())))
                elif times == 1:
                    pass
                else:
                    power = int(log2(times))
                    remainder = int(times - 2 ** power)
                    new_var = new_variable()
                    bisect.insort(free_temporary_variable,
                                  new_var, key=lambda x: x.index)
                    if remainder != 0:
                        operations.append(
                            (new_var, Operator("", Token.empty()), left_var))
                    operations.extend(
                        [(left_var, Operator("*", Token.empty()), left_var)] * power)
                    operations.extend(
                        [(left_var, Operator("*", Token.empty()),
                          new_var)] * remainder)
            else:
                operations.append((left_var, node.operator, right_var))
            return left_var
        elif isinstance(left_var, Constant) and isinstance(right_var, Constant):
            const = Constant(eval_expr(left_var.content +
                                       node.content + right_var.content), Token.empty())
            if is_first_time:
                output_variable = new_variable()
                operations.append(
                    (output_variable, Operator("", Token.empty()), const))
            return const

        new_var = new_variable()
        if is_first_time:
            output_variable = new_var
        if isinstance(right_var, TemporaryVariable):
            bisect.insort(free_temporary_variable,
                          right_var, key=lambda x: x.index)
        if not can_inject or output.content != left_var.content:
            operations.append(
                (new_var, Operator("", Token.empty()), left_var))
        if node.content == "**":
            if not isinstance(right_var, Constant):
                raise JMCSyntaxException(
                    "Power operator (**) only works on a constant", right_var.token, tokenizer)
            times = float(right_var.content)
            if times < 0:
                raise JMCSyntaxException(
                    "Power operator (**) only works on a positive number as there's no float in minecraft scoreboard", right_var.token, tokenizer)
            elif not times.is_integer():
                raise JMCSyntaxException(
                    "Power operator (**) only works on a whole integer", right_var.token, tokenizer)
            elif times == 0:
                operations.append(
                    (new_var, Operator("", Token.empty()), Constant("1", Token.empty())))
            elif times == 1:
                pass
            else:
                power = int(log2(times))
                remainder = int(times - 2 ** power)
                new_var2 = new_variable()
                bisect.insort(free_temporary_variable,
                              new_var, key=lambda x: x.index)
                if remainder != 0:
                    operations.append(
                        (new_var2, Operator("", Token.empty()), new_var))
                operations.extend(
                    [(new_var, Operator("*", Token.empty()), new_var)] * power)
                operations.extend(
                    [(new_var, Operator("*", Token.empty()),
                      new_var2)] * remainder)
        else:
            operations.append((new_var, node.operator, right_var))
        return new_var

    _tree_to_operation(tree)
    output_variable = cast(TemporaryVariable | None, output_variable)
    assert output_variable is not None
    if can_inject:
        output_variable.content = output.content
        output_variable.index = -1

    max_index = 0
    for temporary_variable in all_temporary_variable:
        if temporary_variable.index == -1:
            continue
        temporary_variable.index = max_index
        temporary_variable.content = f"__temp{max_index}__ {DataPack.var_name}"
        max_index += 1
    if not can_inject:
        operations.append(
            (output, Operator("", Token.empty()), output_variable))
    return operations


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()


def search_for_output_in_tree(tree: Expression, output: Variable) -> bool:
    """
    Return whether output variable can be injected directly into operations
    (happens when there's no output in tree or when there's only 1 and tree can be swapped)
    """
    path: list[tuple[Expression, Direction]] = []
    output_path: list[tuple[Expression, Direction]] | None = None

    is_return_false = False

    def _walk(node: Node):
        nonlocal is_return_false
        if is_return_false:
            return
        if isinstance(node, Expression):
            path.append((node, Direction.LEFT))
            _walk(node.children[0])
            path.pop()
            path.append((node, Direction.RIGHT))
            _walk(node.children[1])
            path.pop()
        elif isinstance(node, Variable) and node.content == output.content:
            nonlocal output_path
            if output_path is not None:
                is_return_false = True
            output_path = path.copy()

    _walk(tree)
    if is_return_false:
        return False

    output_path = cast(list[tuple[Expression, Direction]] | None, output_path)
    if output_path is None:
        return True

    for node, direction in output_path:
        if direction == Direction.LEFT:
            continue
        elif direction == Direction.RIGHT:
            if not node.operator.is_reflective():
                return False
    for node, direction in output_path:
        if direction == Direction.LEFT:
            continue
        elif direction == Direction.RIGHT:
            node.children = (node.children[1], node.children[0])
    return True


def optimize_const(operations: list[tuple[Variable, Operator, Number]]) -> list[tuple[Variable, Operator, Number]]:
    temp_operations: list[tuple[Variable, Operator, Number]] = []
    new_operations: list[tuple[Variable, Operator, Number]] = []
    for var, op, num in operations:
        if not temp_operations:
            temp_operations.append((var, op, num))
            continue
        is_same_var = temp_operations and var.content == temp_operations[0][0].content
        is_same_op_group = temp_operations and op.is_same_group(
            temp_operations[-1][1])
        is_after_equal = len(
            temp_operations) == 1 and temp_operations[0][1].content == ""
        if is_same_var and (is_same_op_group or is_after_equal):
            temp_operations.append((var, op, num))
            continue

        saved_operation = (var, op, num)

        first_const_index = -1
        indices_to_delete: list[int] = []
        for i, (var, op, num) in enumerate(temp_operations):
            if not isinstance(num, Constant):
                continue
            if first_const_index == -1:
                first_const_index = i
                continue
            const = temp_operations[first_const_index][2]
            temp_operations[first_const_index] = (temp_operations[first_const_index][0], temp_operations[first_const_index][1], Constant(
                eval_expr(const.content + op.content + " " + num.content), const.token))
            indices_to_delete.append(i)

            if first_const_index != -1:
                if temp_operations[first_const_index][1].content == "*%" and int(temp_operations[first_const_index][2].content) == 1:
                    indices_to_delete.insert(0, first_const_index)
                if temp_operations[first_const_index][1].content == "+-" and int(temp_operations[first_const_index][2].content) == 0:
                    indices_to_delete.insert(0, first_const_index)

        for i in reversed(indices_to_delete):
            del temp_operations[i]

        new_operations.extend(temp_operations)
        temp_operations = [saved_operation]
    if temp_operations:
        first_const_index = -1
        indices_to_delete: list[int] = []
        for i, (var, op, num) in enumerate(temp_operations):
            if not isinstance(num, Constant):
                continue
            if first_const_index == -1:
                first_const_index = i
                continue
            const = temp_operations[first_const_index][2]
            temp_operations[first_const_index] = (temp_operations[first_const_index][0], temp_operations[first_const_index][1], Constant(
                eval_expr(const.content + op.content + " " + num.content), const.token))
            indices_to_delete.append(i)
        print(first_const_index)
        print(temp_operations[first_const_index][1].content)
        print(temp_operations[first_const_index][2].content)
        if first_const_index != -1:
            if temp_operations[first_const_index][1].content in "*%" and int(temp_operations[first_const_index][2].content) == 1:
                indices_to_delete.insert(0, first_const_index)
            elif temp_operations[first_const_index][1].content in "+-" and int(temp_operations[first_const_index][2].content) == 0:
                print("yeah")
                indices_to_delete.insert(0, first_const_index)

        for i in reversed(indices_to_delete):
            del temp_operations[i]
        new_operations.extend(temp_operations)
    return new_operations
