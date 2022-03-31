from dataclasses import dataclass, field
from ast import literal_eval
from typing import Optional
from enum import Enum
from json import dumps
import re

from .exception import JMCSyntaxException, JMCSyntaxWarning
from .log import Logger


logger = Logger(__name__)


class TokenType(Enum):
    keyword = "Keyword"
    paren = "Parentheses"
    paren_round = "RoundParentheses"
    paren_square = "SquareParentheses"
    paren_curly = "CurlyParentheses"
    string = "StringLiteral"
    comment = "Comment"
    comma = "Comma"
    func = "Function"


@dataclass(frozen=True, eq=False)
class Token:
    token_type: TokenType
    line: int
    col: int
    string: str
    _length: Optional[int] = field(init=False, repr=False, default=None)

    @property
    def length(self) -> int:
        if self._length is None:
            object.__setattr__(self, "_length", len(
                self.string)+2 if self.token_type == TokenType.string else len(self.string))
        return self._length


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
    COMMA = ","
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
    line: int
    col: int

    state: Optional[TokenType]
    token: str
    token_pos: Optional[Pos]
    keywords: list[Token]

    list_of_tokens: list[list[Token]]

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

    def __init__(self, raw_string: str, file_path_str: str, line: int = 1, col: int = 1, file_string: str = None, expect_semicolon: bool = True) -> None:
        logger.debug("Initializing Tokenizer")
        self.raw_string = raw_string
        if file_string is None:
            self.file_string = raw_string
        else:
            self.file_string = file_string
        self.file_path = file_path_str
        self.programs = self.parse(
            self.raw_string, line=line, col=col, expect_semicolon=expect_semicolon)

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
            logger.debug(f"Appending keywords: {self.keywords}")
            self.list_of_tokens.append(self.keywords)
            self.keywords = []
        else:
            raise JMCSyntaxWarning(
                f"In {self.file_path}\nUnnecessary semicolon(;) at line {self.line} col {self.col}.\n{self.raw_string.split(Re.NEW_LINE)[self.line-1][:self.col]} <-")

    def parse(self, string: str, line: int, col: int, expect_semicolon: bool) -> list[list[Token]]:
        self.list_of_tokens = []
        self.line = line
        self.col = col - 1
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

        for char in string:
            self.col += 1
            if not expect_semicolon and char == Re.SEMICOLON and self.state in [TokenType.keyword, None]:
                raise JMCSyntaxException(
                    "Unexpected semicolon(;)", self, self, display_col_length=False)

            if char == Re.NEW_LINE:
                if self.state == TokenType.string:
                    raise JMCSyntaxException(
                        "String literal contains an unescaped line break.", self, self, entire_line=True)
                elif self.state == TokenType.comment:
                    self.state = None
                elif self.state == TokenType.keyword:
                    self.append_token()
                elif self.state == TokenType.paren:
                    self.token += char
                self.line += 1
                self.col = 0
                continue

            if char == Re.SLASH and self.is_slash and self.state != TokenType.paren:
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
                    Re.COMMA
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
                        "Unexpected bracket", self, self, display_col_length=False)
                elif char == Re.HASH and self.col == 1:
                    self.state = TokenType.comment
                elif char == Re.COMMA:
                    self.token += char
                    self.token_pos = Pos(self.line, self.col)
                    self.state = TokenType.comma
                    self.append_token()
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
                        if is_end and expect_semicolon:
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

        if not expect_semicolon:
            if self.token != "":
                self.append_token()
            if self.keywords:
                self.append_keywords()

        if self.state == TokenType.string:
            raise JMCSyntaxException(
                f"In {self.file_path}\nString literal at line {self.line} contains an unescaped line break.\n{self.raw_string.split(Re.NEW_LINE)[self.line-1]} <-")
        elif self.state == TokenType.paren:
            raise JMCSyntaxException(
                f"In {self.file_path}\nBracket at line {self.token_pos.line} col {self.token_pos.col} was never closed.\n{self.raw_string.split(Re.NEW_LINE)[self.token_pos.line-1][:self.token_pos.col]} <-")
        elif self.keywords:
            raise JMCSyntaxException(
                f"In {self.file_path}\nExpected semicolon(;) at line {self.keywords[-1].line} col {self.keywords[-1].col+self.keywords[-1].length}.\n{self.raw_string.split(Re.NEW_LINE)[self.keywords[-1].line-1][:self.keywords[-1].col+self.keywords[-1].length-1]} <-")

        return self.list_of_tokens

    def split_token(self, token: Token, split_str: str) -> list[Token]:
        """Split a keyword token into multiple tokens"""
        if token.token_type != TokenType.keyword:
            raise ValueError(
                f"Called split_token on non-keyword token."
            )
        strings = []
        for string in token.string.split(split_str):
            if string:
                strings.append(string)
            strings.append(split_str)
        strings = strings[:-1]
        tokens = []
        col = token.col
        for string in strings:
            tokens.append(Token(TokenType.keyword, token.line, col, string))
            col += len(string)
        return tokens

    def split_tokens(self, tokens: list[Token], split_strings: list[str]) -> list[Token]:
        """Loop through all tokens and split a keyword token thta contain string inside split_strings"""
        for split_str in split_strings:
            new_tokens = []
            for token in tokens:
                if token.token_type == TokenType.keyword:
                    new_tokens.extend(self.split_token(token, split_str))
                else:
                    new_tokens.append(token)
            tokens = new_tokens
        return tokens

    def find_token(self, tokens: list[Token], string: str) -> list[list[Token]]:
        """Split tokens by token that match the string"""
        result: list[list[Token]] = []
        token_array: list[Token] = []
        for token in tokens:
            if token.string == string and token.token_type == TokenType.keyword:
                result.append(token_array)
                token_array = []
            else:
                token_array.append(token)

        result.append(token_array)
        return result

    def find_tokens(self, tokens: list[Token], string: str) -> list[list[Token]]:
        """Splot tokens by set of tokens that can combined into the string"""
        state = 0
        max_state = len(string)
        result: list[list[Token]] = []
        token_array: list[Token] = []
        temp_array: list[Token] = []
        for token in tokens:
            if token.token_type != TokenType.keyword:
                state = 0
                token_array.extend(temp_array)
                token_array.append(token)
                temp_array = []
                continue
            if token.string == string[state]:
                state += 1
                temp_array.append(token)
                if state == max_state:
                    state = 0
                    result.append(token_array)
                    token_array = []
                    temp_array = []
            else:
                state = 0
                token_array.extend(temp_array)
                token_array.append(token)
                temp_array = []

        token_array.extend(temp_array)
        result.append(token_array)
        return result

    def merge_tokens(self, tokens: list[Token], string: str) -> list[Token]:
        """Loop through tokens and merge tokens that can be combined into string"""
        state = 0
        max_state = len(string)
        result: list[Token] = []
        token_array: list[Token] = []
        for token in tokens:
            if token.token_type != TokenType.keyword:
                state = 0
                result.extend(token_array)
                result.append(token)
                token_array = []
                continue
            if token.string == string[state]:
                if token_array:
                    if token.line != token_array[-1].line or token.col-1 != token_array[-1].col:
                        state = 0
                        result.extend(token_array)
                        result.append(token)
                        token_array = []
                        continue
                state += 1
                token_array.append(token)
                if state == max_state:
                    state = 0
                    result.append(
                        Token(TokenType.keyword, token_array[0].line, token_array[0].col, string))
                    token_array = []
            else:
                state = 0
                result.extend(token_array)
                result.append(token)
                token_array = []

        result.extend(token_array)
        return result

    def parse_func_args(self, token: Token) -> tuple[list[Token], dict[str, Token]]:
        if token.token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                f"In {self.file_path}\nExpected ( at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[self.line-1]} <-"
            )
        keywords = self.parse(
            token.string[1:-1], line=token.line, col=token.col, expect_semicolon=False)[0]
        keywords = self.split_tokens(keywords, ['='])
        keywords = self.merge_tokens(keywords, '=>')
        args: list[Token] = []
        kwargs: dict[str, Token] = dict()
        key: str = ""
        arg: str = ""
        arrow_func_state = 0
        """
        0: None
        1: ()
        2: =>
        """

        def add_arg(token: Token, from_comma: bool = False) -> None:
            nonlocal arg
            nonlocal args
            nonlocal expecting_comma
            expecting_comma = False
            if kwargs:
                raise JMCSyntaxException(
                    f"In {self.file_path}\nPositional argument follows keyword argument at line {token.line} col {token.col+1}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col+1]} <-"
                )
            args.append(Token(string=arg, line=token.line,
                              col=token.col, token_type=token.token_type))
            arg = ""

        def add_kwarg(token: Token) -> None:
            nonlocal key
            nonlocal arg
            nonlocal kwargs
            nonlocal expecting_comma
            expecting_comma = True
            if key[0] in [Paren.L_CURLY, Paren.L_ROUND, Paren.L_SQUARE]:
                raise JMCSyntaxException(
                    f"In {self.file_path}\nInvalid key({key}) at line {last_token.line} col {last_token.col}.\n{self.raw_string.split(Re.NEW_LINE)[last_token.line-1][:last_token.col]} <-"
                )
            if key == "":
                raise JMCSyntaxException(
                    f"In {self.file_path}\nEmpty at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col]} <-"
                )

            if key in kwargs:
                raise JMCSyntaxException(
                    f"In {self.file_path}\nDuplicated key({key}) at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col]} <-"
                )
            kwargs[key] = Token(string=arg, line=token.line,
                                col=token.col, token_type=token.token_type)
            key = ""
            arg = ""

        expecting_comma = False
        for token in keywords:
            if expecting_comma and token.token_type != TokenType.comma:
                raise JMCSyntaxException(
                    f"In {self.file_path}\nExpected comma(,) at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col-1]} <-"
                )
            if arrow_func_state > 0:
                if arrow_func_state == 1:
                    if token.string == "=>" and token.token_type == TokenType.keyword:
                        arrow_func_state = 2
                        last_token = token
                        continue
                    else:
                        arg = last_token.string
                        if key:
                            add_kwarg(last_token)
                        arrow_func_state = 0
                        continue
                elif arrow_func_state == 2:
                    if token.token_type == TokenType.paren_curly:
                        new_token = Token(
                            string=token.string[1:-1], line=token.line, col=token.col, token_type=TokenType.func)
                        arg = new_token.string
                        if key:
                            add_kwarg(new_token)
                        last_token = new_token
                        arrow_func_state = 0
                        continue
                    else:
                        raise JMCSyntaxException(
                            f"In {self.file_path}\nExpected {'{'} at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col]} <-"
                        )

            if token.token_type == TokenType.keyword:
                if arg:
                    if token.string == '=':
                        key = arg
                        arg = ""
                    else:
                        raise JMCSyntaxException(
                            f"In {self.file_path}\nUnexpected token at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col+token.length]} <-"
                        )
                elif key:
                    arg = token.string
                    if token.string == '=':
                        raise JMCSyntaxException(
                            f"In {self.file_path}\nDuplicated equal sign(=) at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col]} <-"
                        )
                    add_kwarg(token)
                else:
                    arg = token.string

            elif token.token_type == TokenType.comma:
                arrow_func_state = 0
                expecting_comma = False
                if arg:
                    add_arg(last_token, from_comma=True)
            elif token.token_type in [TokenType.paren_round, TokenType.paren_curly, TokenType.paren_square]:
                if token.string == "()":
                    arrow_func_state = 1
                else:
                    arg = token.string
                    if key:
                        add_kwarg(token)

            elif token.token_type == TokenType.string:
                if arg:
                    raise JMCSyntaxException(
                        f"In {self.file_path}\nUnexpected token at line {token.line} col {token.col}.\n{self.raw_string.split(Re.NEW_LINE)[token.line-1][:token.col+token.length]} <-"
                    )
                arg = token.string
                if key:
                    add_kwarg(token)
            last_token = token

        if arg:
            add_arg(token)

        return args, kwargs

    def clean_up_paren(self, token: Token, is_nbt: bool = True) -> str:
        if len(token.string) == 2:
            return token.string
        open = token.string[0]
        close = token.string[-1]
        tokenizer = Tokenizer(token.string[1:-1], self.file_path, token.line,
                              token.col, self.file_string, expect_semicolon=False)
        string = ""
        if open == '{' and tokenizer.programs[0][0].token_type == TokenType.string:
            is_nbt = False
        for token_ in tokenizer.programs[0]:
            if token_.token_type in [TokenType.paren_curly, TokenType.paren_round, TokenType.paren_square]:
                string += tokenizer.clean_up_paren(token_, is_nbt)
            elif token_.token_type == TokenType.string:
                if is_nbt:
                    string += repr(token_.string)
                else:
                    string += dumps(token_.string)
            else:
                string += token_.string
        return open+string+close
