from dataclasses import dataclass
from ast import literal_eval
from distutils import command
from typing import Optional
from enum import Enum
import re

from .exception import JMCSyntaxException


class TokenType(Enum):
    keyword = "Keyword"
    paren = "Parentheses"
    paren_round = "RoundParentheses"
    paren_square = "SquareParentheses"
    paren_curly = "CurlyParentheses"
    string = "StringLiteral"
    comment = "Comment"


@dataclass(frozen=True, eq=False)
class Token:
    token_type: TokenType
    line: int
    col: int
    string: str


@dataclass(frozen=True, eq=False)
class Pos:
    line: int
    col: int


class Re:
    NEW_LINE = '\n'
    BACKSLASH = '\\'
    WHITESPACE = r'\s+'
    KEYWORD = r'[a-zA-Z0-9_\.\/\^\~]'
    SEMICOLON = ';'
    HASH = '#'
    SLASH = "/"


class Quote:
    SINGLE = "'"
    DOUBLE = '"'


class Paren:
    L_ROUND = '('
    R_ROUND = ')'
    L_SQUARE = '['
    R_SQUARE = ']'
    L_CURLY = '{'
    R_CURLY = '}'


PAREN_PAIR = {
    Paren.L_CURLY: Paren.R_CURLY,
    Paren.L_SQUARE: Paren.R_SQUARE,
    Paren.L_ROUND: Paren.R_ROUND,
}


class Tokenizer:
    line = 1
    col = 0

    state: Optional[TokenType]
    token: str
    token_pos: Optional[Pos]
    keywords: list[Token]

    # String
    quote: Optional[str]
    is_escaped: bool
    """Is it an escaped character (Backslashed)"""

    # Parenthesis
    paren: Optional[str]
    r_paren: Optional[str]
    paren_count: Optional[int]
    is_string: bool

    # Comment
    is_slash: bool

    def __init__(self, raw_string: str, file_name: str) -> None:
        self.raw_string = raw_string
        self.programs: list[list[Token]] = []
        self.file_name = file_name
        self.parse()

    def append_token(self) -> None:
        self.keywords.append(
            Token(self.state,
                  self.token_pos.line,
                  self.token_pos.col,
                  self.token)
        )
        self.token = ""
        self.token_pos = None
        self.state = None

    def append_keywords(self) -> None:
        if len(self.keywords) != 0:
            self.programs.append(self.keywords)
            self.keywords = []

    def parse(self) -> None:
        self.keywords = []
        self.state = None
        self.token = ""
        self.token_pos = None
        # String
        self.quote = None
        self.is_escaped = False
        # Parenthesis
        self.paren = None
        self.r_paren = None
        self.paren_count = None
        self.is_string = False
        # Comment
        self.is_slash = False

        for char in self.raw_string:
            self.col += 1
            if char == Re.NEW_LINE:
                if self.state == TokenType.string:
                    raise JMCSyntaxException(
                        f"In {self.file_name}\nString literal at line {self.line} contains an unescaped line break.\n{self.raw_string.split(Re.NEW_LINE)[self.line-1]} <-")
                if self.state == TokenType.comment:
                    self.state = None
                if self.state == TokenType.keyword:
                    self.append_token()
                self.line += 1
                self.col = 0
                continue

            if char == Re.SLASH and self.is_slash and self.state != TokenType.string:
                self.state = TokenType.comment
                self.token = self.token[:-1]
                continue

            if self.state == TokenType.keyword:
                if char in [
                    Quote.SINGLE,
                    Quote.DOUBLE,
                    Paren.L_CURLY,
                    Paren.L_ROUND,
                    Paren.L_SQUARE,
                    Re.SEMICOLON,
                ] or re.match(Re.WHITESPACE, char):
                    self.append_token()
                else:
                    self.token += char
                    continue

            if self.state == None:

                if char in [Quote.SINGLE, Quote.DOUBLE]:
                    self.state = TokenType.string
                    self.token_pos = Pos(self.line, self.col)
                    self.quote = char
                    self.token += char
                elif re.match(Re.WHITESPACE, char):
                    continue
                elif char == Re.SEMICOLON:
                    self.append_keywords()
                elif char in [Paren.L_CURLY, Paren.L_ROUND, Paren.L_SQUARE]:
                    self.state = TokenType.paren
                    self.token += char
                    self.token_pos = Pos(self.line, self.col)
                    self.paren = char
                    self.r_paren = PAREN_PAIR[char]
                    self.paren_count = 0
                elif char in [Paren.R_CURLY, Paren.R_ROUND, Paren.R_SQUARE]:
                    raise JMCSyntaxException(
                        f"In {self.file_name}\nUnexpected bracket at line {self.line} col {self.col}.\n{self.raw_string.split(Re.NEW_LINE)[self.line-1][:self.col]} <-")
                elif char == Re.HASH and self.col == 1:
                    self.state = TokenType.comment
                else:
                    self.state = TokenType.keyword
                    self.token_pos = Pos(self.line, self.col)
                    self.token += char

            elif self.state == TokenType.string:
                self.token += char
                if char == Re.BACKSLASH and not self.is_escaped:
                    self.is_escaped = True
                elif char == self.quote and not self.is_escaped:
                    self.token = literal_eval(self.token)
                    self.append_token()
                elif self.is_escaped:
                    self.is_escaped = False

            elif self.state == TokenType.paren:
                self.token += char
                if self.is_string:
                    if char == Re.BACKSLASH and not self.is_escaped:
                        self.is_escaped = True
                    elif char == self.quote and not self.is_escaped:
                        self.is_string = False
                    elif self.is_escaped:
                        self.is_escaped = False
                else:
                    if char == self.r_paren and self.paren_count == 0:
                        is_end = False
                        if self.paren == Paren.L_CURLY:
                            self.state = TokenType.paren_curly
                            is_end = True
                        elif self.paren == Paren.L_ROUND:
                            self.state = TokenType.paren_round
                        elif self.paren == Paren.L_SQUARE:
                            self.state = TokenType.paren_square
                        self.append_token()
                        if is_end:
                            self.append_keywords()
                        continue

                    if char == self.paren:
                        self.paren_count += 1
                    elif char == self.r_paren:
                        self.paren_count -= 1
                    elif char in [Quote.SINGLE, Quote.DOUBLE]:
                        self.is_string = True
                        self.quote = char

            elif self.state == TokenType.comment:
                pass

            self.is_slash = (char == Re.SLASH)

        if self.state == TokenType.string:
            raise JMCSyntaxException(
                f"In {self.file_name}\nString literal at line {self.line} contains an unescaped line break.\n{self.raw_string.split(Re.NEW_LINE)[self.line-1]} <-")
        elif self.state == TokenType.paren:
            raise JMCSyntaxException(
                f"In {self.file_name}\nBracket at line {self.token_pos.line} col {self.token_pos.col} was never closed.\n{self.raw_string.split(Re.NEW_LINE)[self.token_pos.line-1][:self.token_pos.col]} <-")
        elif len(self.keywords) != 0:
            raise JMCSyntaxException(
                f"In {self.file_name}\nExpected semicolon(;) at line {self.line} (at the end of the file).")
