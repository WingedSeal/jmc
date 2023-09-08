import ast
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Content:
    """
    Content returned from isolated environment
    """
    __content: list[str] = field(default_factory=list, init=False)
    get_command_function: str | None = field(default=None, init=False)
    """Content in form of list of command"""

    def __init__(self) -> None:
        self.__content = []

    def add_command(self, content: str) -> list[str]:
        if not isinstance(content, str):
            raise ValueError(
                f"{self.get_command_function} expected str, got {content.__class__.__name__}")
        self.__content.append(str(content))
        return self.__content

    def get_content(self) -> str:
        """Content in form of list of command"""
        content = "\n".join(self.__content)
        self.__content = []
        return content


ALLOWED_MODULE = {
    "itertools",
    "collections",
    "copy",
    "functools",
    "math",
    "random",
    "abc"
}
"""Set of string of module that's allowed"""


class NodeTransformer(ast.NodeTransformer):

    def __init__(self) -> None:
        pass

    def visit_Import(self, node: ast.Import) -> ast.Import:
        if node.names[0].name in ALLOWED_MODULE:
            return node
        raise ImportError(
            f"Unable to import {node.names[0].name} module in JMC.")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        if node.module in ALLOWED_MODULE:
            return node
        raise ImportError(f"Unable to import {node.module} module in JMC.")


@dataclass(frozen=True, slots=True)
class IsolatedEnvironment:
    """
    Isolated environment for running python
    """
    content: Content = field(default_factory=Content, init=False)
    exec_global: dict[str | None, dict[str, Any]] = field(
        default_factory=dict, init=False)
    get_command_function: str

    def run(self, code: str, environment_id: str | None = None) -> str:
        """
        Run code on isloated environment

        :param code: Code to be run
        :param environment_id: ID of the environment, same id will share the same environment
        :return: Commands that the code return back with add_command
        """
        self.content.get_command_function = self.get_command_function
        compiled = compile(
            NodeTransformer().visit(ast.parse(code)),
            filename="<ast>",
            mode='exec')
        if environment_id not in self.exec_global:
            self.exec_global[environment_id] = {
                self.get_command_function: self.content.add_command}
        exec(compiled, self.exec_global[environment_id])
        return self.content.get_content()
