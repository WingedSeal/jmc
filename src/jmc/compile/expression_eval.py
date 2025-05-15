from dataclasses import dataclass
import bisect
from typing import cast


class OpenBracket:
    def get_order(self) -> int:
        return 0


OPEN_BRACKET = OpenBracket()


@dataclass
class Node:
    content: str


@dataclass
class Operator(Node):
    def get_order(self) -> int:
        if self.content == "^":
            return 30
        elif self.content in "*/%":
            return 20
        elif self.content in "+-":
            return 10
        else:
            raise Exception(self.content)

    def is_reflective(self) -> bool:
        if self.content in "+*":
            return True
        elif self.content in "-/%^":
            return False
        else:
            raise Exception(self.content)


@dataclass
class Number(Node):
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


def is_int(s: str):
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


def expression_to_tree(expression: list[str]) -> Expression:
    operator_stack: list[Operator | OpenBracket] = []
    number_stack: list[Number] = []

    def process_stack():
        while operator_stack:
            operator = operator_stack.pop()
            if isinstance(operator, OpenBracket):
                break
            if len(number_stack) < 2:
                raise Exception()
            right = number_stack.pop()
            left = number_stack.pop()
            number_stack.append(Expression(
                operator.content, (left, right), operator))

    for char in expression:
        if is_int(char):
            number_stack.append(Constant(char))
        elif char in "+-*/%^":
            operator = Operator(char)
            if operator_stack and operator.get_order() < operator_stack[-1].get_order():
                process_stack()
            operator_stack.append(operator)
        elif char == "(":
            operator_stack.append(OPEN_BRACKET)
        elif char == ")":
            process_stack()
        else:
            number_stack.append(Variable(char))
    process_stack()
    if len(number_stack) > 1:
        raise Exception()
    assert isinstance(number_stack[0], Expression)
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


def tree_to_operations(tree: Expression) -> list[tuple[Variable, Operator, Number]]:
    operations: list[tuple[Variable, Operator, Number]] = []
    max_index = 0
    free_temporary_variable: list[TemporaryVariable] = []
    all_temporary_variable: list[TemporaryVariable] = []
    output_variable: TemporaryVariable | None = None

    def new_variable() -> TemporaryVariable:
        if free_temporary_variable:
            return free_temporary_variable.pop(0)
        nonlocal max_index
        max_index += 1
        temporary_variable = TemporaryVariable(
            "", max_index)
        all_temporary_variable.append(temporary_variable)
        return temporary_variable

    def _tree_to_operation(node: Number, is_first_time: bool = True) -> Number:
        if isinstance(node, Expression):
            nonlocal output_variable
            left_var = _tree_to_operation(node.children[0], False)
            right_var = _tree_to_operation(node.children[1], False)
            if isinstance(left_var, TemporaryVariable):
                if is_first_time:
                    output_variable = left_var
                if isinstance(right_var, TemporaryVariable):
                    bisect.insort(free_temporary_variable,
                                  right_var, key=lambda x: x.index)
                if node.content == "^":
                    if not isinstance(right_var, Constant):
                        raise Exception("^ only works on const")
                    times = int(right_var.content)
                    if times < 0:
                        raise Exception("no float here")
                    elif times == 0:
                        operations.append(
                            (left_var, Operator(""), Constant("1")))
                    else:
                        operations.extend(
                            [(left_var, Operator("*"), left_var)] * (times - 1))
                else:
                    operations.append((left_var, node.operator, right_var))
                return left_var
            elif isinstance(left_var, Constant) and isinstance(right_var, Constant):
                const = Constant(left_var.content +
                                 node.content + right_var.content)  # TODO: Evaluate
                if is_first_time:
                    output_variable = new_variable()
                    operations.append((output_variable, Operator(""), const))
                return const

            else:
                new_var = new_variable()
                if is_first_time:
                    output_variable = new_var
                if isinstance(right_var, TemporaryVariable):
                    bisect.insort(free_temporary_variable,
                                  right_var, key=lambda x: x.index)
                operations.append((new_var, Operator(""), left_var))
                if node.content == "^":
                    if not isinstance(right_var, Constant):
                        raise Exception("^ only works on const")
                    times = int(right_var.content)
                    if times < 0:
                        raise Exception("no float here")
                    elif times == 0:
                        operations.append(
                            (new_var, Operator(""), Constant("1")))
                    else:
                        operations.extend(
                            [(new_var, Operator("*"), new_var)] * (times - 1))
                else:
                    operations.append((new_var, node.operator, right_var))
                return new_var
        return node

    _tree_to_operation(tree)
    output_variable = cast(TemporaryVariable | None, output_variable)
    assert output_variable is not None
    output_variable.content = "OUTPUT"
    output_variable.index = -1

    max_index = 0
    for temporary_variable in all_temporary_variable:
        if temporary_variable.index == -1:
            continue
        temporary_variable.index = max_index
        temporary_variable.content = f"_t{max_index}"
        max_index += 1
    return operations


tree = expression_to_tree(list("b^0+1"))
print_tree(tree)

for op in tree_to_operations(tree):
    print(op[0].content, op[1].content + "=", op[2].content)
