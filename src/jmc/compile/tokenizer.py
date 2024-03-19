from copy import deepcopy
from dataclasses import dataclass
from ast import literal_eval
from enum import Enum
import re
from typing import TYPE_CHECKING


from .utils import is_connected, is_decorator
from .header import MacroFactory, Header
from .exception import JMCSyntaxException, JMCSyntaxWarning
from .log import Logger

if TYPE_CHECKING:
    from ..compile.lexer import Lexer

logger = Logger(__name__)

NEW_LINE = "\n"

TERMINATE_LINE = {
    "function",
    "class",
    "new",
    "schedule",
    "if",
    "else",
    "do",
    "while",
    "for",
    "switch"
}


class TokenType(Enum):
    KEYWORD = "Keyword"
    OPERATOR = "Operator"
    """`+ - * / > < = % : ! | &`"""
    PAREN = "Parentheses"
    PAREN_ROUND = "RoundParentheses"
    PAREN_SQUARE = "SquareParentheses"
    PAREN_CURLY = "CurlyParentheses"
    STRING = "StringLiteral"
    COMMENT = "Comment"
    COMMA = "Comma"
    FUNC = "Function"


@dataclass(frozen=True, eq=False, slots=True)
class Token:
    """
    A dataclass containing information for Token for Lexical Analysis

    :param token_type: Type of the token
    :param line: Which line it's found in
    :param col: Which column it's found in
    :param string: The string representation (including parentheses, excluding quotation mark)
    """
    token_type: TokenType
    line: int
    col: int
    string: str
    """The string representation (including parentheses, excluding quotation mark)"""
    _macro_length: int = 0
    quote: str = ""

    # def __new__(cls: type["Token"], token_type: TokenType, line: int, col: int, string: str) -> "Token":
    #     return super().__new__(cls)

    def __post_init__(self) -> None:
        """
        Edit string and _length according to macros(`#define something`) defined
        """
        if self.token_type == TokenType.PAREN_CURLY:
            if not self.string.startswith(
                    "{") or not self.string.endswith("}"):
                raise ValueError(
                    "paren_curly Token created but string doesn't start and end with the parenthesis")

    @property
    def length(self) -> int:
        """
        Getting the length of the string in token(including quotation mark)

        :return: Length of the string
        """
        # if not self._macro_length:
        return len(repr(self.string)) if self.token_type == TokenType.STRING else len(
            self.string)
        # else:
        #     return self._macro_length

    def add_quotation(self) -> str:
        """Get self.string including quotation mark (Raise error when the token_type is not TokenType.STRING)"""
        if self.token_type != TokenType.STRING:
            raise ValueError("TokenType is not STRING in Token.add_quitation")

        return repr(self.string)

    def get_full_string(self) -> str:
        """Get self.string including quotation mark"""
        if self.token_type == TokenType.STRING:
            if self.quote == "`":
                return "`\n" + repr(self.string)[1:-1] + "\n`"
            return repr(self.string)
        return self.string

    @classmethod
    def empty(cls, string: str = "",
              token_type: TokenType = TokenType.KEYWORD) -> "Token":
        """
        Create an empty token

        :param string: New token's string, defaults to ""
        :param token_type: New token's TokenType, defaults to TokenType.KEYWORD
        :return: New token
        """
        return cls(token_type, -1, -1, string)


@dataclass(frozen=True, eq=False, slots=True)
class Pos:
    """
    Dataclass containing line and column
    :var line:
    :var col:
    """
    line: int
    col: int


class Re:
    NEW_LINE = "\n"
    BACKSLASH = "\\"
    WHITESPACE = r"\s+"
    KEYWORD = r"[a-zA-Z0-9_\.\/\^\~]"
    SEMICOLON = ";"
    COMMA = ","
    HASH = "#"
    SLASH = "/"
    TWO_SLASH = SLASH * 2


class Quote:
    SINGLE = "'"
    DOUBLE = '"'
    BACKTICK = "`"


class Paren:
    L_ROUND = "("
    R_ROUND = ")"
    L_SQUARE = "["
    R_SQUARE = "]"
    L_CURLY = "{"
    R_CURLY = "}"


PAREN_PAIR = {
    Paren.L_CURLY: Paren.R_CURLY,
    Paren.L_SQUARE: Paren.R_SQUARE,
    Paren.L_ROUND: Paren.R_ROUND,
}
"""Dictionary of left bracket(string) and right bracket(string)"""

OPERATORS = {"+", "-", "*", "/", ">", "<", "=", "%", ":", "!", "|", "&", "?"}


class Tokenizer:
    """
    A class for converting string into tokens

    :param raw_string: Raw string read from file/given from another tokenizer
    :param file_path_str: File path to current JMC function as string
    :param line: Current line, defaults to 1
    :param col: Current column, defaults to 1
    :param file_string: Entire string read from current file, defaults to None
    :param expect_semicolon: Whether to expect semicolon at the end, defaults to True
    :param allow_semicolon: Whether to allow semicolon at the 2nd char(For minecraft array `[I;int, ...]`), defaults to False
    """
    __slots__ = ("line", "col", "state",
                 "token_str", "token_pos", "keywords",
                 "list_of_keywords", "quote", "is_escaped",
                 "paren", "r_paren", "paren_count",
                 "is_string", "is_slash", "raw_string",
                 "file_string", "file_path", "programs",
                 "is_comment", "allow_semicolon", "macro_factory")

    programs: list[list[Token]]
    """List of lines(list of tokens)"""

    line: int
    """Starts at 1"""
    col: int
    """Starts at 1"""

    state: TokenType | None
    """Current TokenType"""
    token_str: str
    """Current string for token"""
    token_pos: Pos | None
    """Position for creating token"""
    keywords: list[Token]
    """Current list of tokens"""

    list_of_keywords: list[list[Token]]
    """List of keywords(list_of_tokens)"""

    # String
    quote: str | None
    """Type of quote"""
    is_escaped: bool
    """Whether it is an escaped character (Backslashed)"""

    # Parenthesis
    paren: str | None
    """Type of left parenthesis"""
    r_paren: str | None
    """Type of matching right parenthesis"""
    paren_count: int
    """Count of left parenthesis / Count of current layer"""
    is_string: bool
    """Whether the current character is in string (For paren TokenType)"""
    is_comment: bool
    """Whether the current character is in comment (For paren TokenType)"""

    # Comment
    is_slash: bool
    """Whether there's a slash infront of the current character"""

    # Special Case
    allow_semicolon: bool
    """Whether to allow semicolon at the next char(For minecraft array `[I;int, ...]`)"""
    macro_factory: tuple[str, MacroFactory, int, Pos] | None
    """Tuple of (Macro's name and MacroFactory and argument count and the position)"""

    def __init__(self, raw_string: str, file_path_str: str, line: int = 1, col: int = 1,
                 file_string: str | None = None, expect_semicolon: bool = True, allow_semicolon: bool = False) -> None:
        logger.debug("Initializing Tokenizer")
        self.macro_factory = None
        self.allow_semicolon = allow_semicolon
        self.raw_string = raw_string
        if file_string is None:
            self.file_string = raw_string
        else:
            self.file_string = file_string
        self.file_path = file_path_str
        self.programs = self.parse(
            self.raw_string, line=line, col=col, expect_semicolon=expect_semicolon)

    def append_token(self) -> None:
        """
        Append the current token into self.keywords
        """
        header = Header()
        if self.state is None:
            raise ValueError(
                "Tokenizer.append_token() called but Tokenizer.state is still None")
        if self.token_pos is None:
            raise ValueError(
                "Tokenizer.token_pos() called but Tokenizer.token_pos is still None")
        quote = ""
        if self.quote == Quote.BACKTICK:
            quote = self.quote
        new_token = Token(self.state,
                          self.token_pos.line,
                          self.token_pos.col,
                          self.token_str, quote=quote)
        if new_token.token_type == TokenType.KEYWORD and new_token.string in header.macros:
            macro_factory, arg_count = header.macros[new_token.string]
            if arg_count == 0:
                self.keywords.extend(
                    macro_factory(
                        [],
                        self.token_pos.line,
                        self.token_pos.col)
                )
            else:
                self.macro_factory = new_token.string, macro_factory, arg_count, self.token_pos
        elif self.macro_factory:
            if new_token.token_type != TokenType.PAREN_ROUND:
                raise JMCSyntaxWarning(
                    f"Expect round bracket after macro factory({self.macro_factory[0]})", new_token, self, display_col_length=False)
            name, macro_factory, arg_count, token_pos = self.macro_factory
            self.macro_factory = None
            args: list[Token] = []
            args_, kwargs = deepcopy(self).parse_func_args(new_token)
            for arg_ in args_:
                if arg_[0].token_type != TokenType.KEYWORD:
                    raise JMCSyntaxException(
                        f"Macro factory arguments can only have a keyword token (got {arg_[0].token_type})", arg_[0], self)
                if len(arg_) > 1:
                    arg_ = [self.merge_tokens(arg_)]

                args.append(arg_[0])
            if kwargs:
                raise JMCSyntaxWarning(
                    f"Macro factory does not support keyword argument ({list(kwargs.keys())[0]}=)", new_token, self)
            if len(args) != arg_count:
                raise JMCSyntaxWarning(
                    f"This Macro factory ({name}) expect {arg_count} arguments (got {len(args)})", new_token, self)
            self.keywords.extend(
                macro_factory(
                    args,
                    token_pos.line,
                    token_pos.col
                )
            )
        else:
            self.keywords.append(new_token)

        self.token_str = ""
        self.token_pos = None
        self.state = None

    def append_keywords(self) -> None:
        """
        Append keywords into list_of_keywords

        :raises JMCSyntaxWarning: Unnecessary semicolon
        """
        if len(self.keywords) != 0:
            logger.debug(f"Appending keywords: {self.keywords}")
            self.list_of_keywords.append(self.keywords)
            self.keywords = []
        else:
            raise JMCSyntaxWarning(
                "Unnecessary semicolon(;)", None, self)

    def __parse_none(self, char: str) -> bool:
        if char in {Quote.SINGLE, Quote.DOUBLE, Quote.BACKTICK}:
            self.state = TokenType.STRING
            self.token_pos = Pos(self.line, self.col)
            self.quote = char
            self.token_str += char
        elif re.match(Re.WHITESPACE, char):
            return True
        elif char == Re.SEMICOLON:
            if self.macro_factory:
                raise JMCSyntaxWarning(
                    f"Expect round bracket after macro factory({self.macro_factory[0]})", None, self)
            self.append_keywords()
        elif char in {Paren.L_CURLY, Paren.L_ROUND, Paren.L_SQUARE}:
            self.state = TokenType.PAREN
            self.token_str += char
            self.token_pos = Pos(self.line, self.col)
            self.paren = char
            self.r_paren = PAREN_PAIR[char]
            self.paren_count = 0
        elif char in {Paren.R_CURLY, Paren.R_ROUND, Paren.R_SQUARE}:
            raise JMCSyntaxException(
                "Unexpected bracket", None, self, display_col_length=False)
        elif char == Re.HASH and not self.keywords:
            self.state = TokenType.COMMENT
        elif char == Re.COMMA:
            self.token_str += char
            self.token_pos = Pos(self.line, self.col)
            self.state = TokenType.COMMA
            self.append_token()
        elif char in OPERATORS:
            self.state = TokenType.OPERATOR
            self.token_pos = Pos(self.line, self.col)
            self.token_str += char
        else:
            self.state = TokenType.KEYWORD
            self.token_pos = Pos(self.line, self.col)
            self.token_str += char
        return False

    def __parse_keyword_and_operator(
            self, char: str, expect_semicolon: bool) -> bool:
        if char in {
            Quote.SINGLE,
            Quote.DOUBLE,
            Paren.L_CURLY,
            Paren.L_ROUND,
            Paren.L_SQUARE,
            Re.COMMA
        } or re.match(Re.WHITESPACE, char):
            self.append_token()
            return False

        if self.state == TokenType.KEYWORD and char in OPERATORS:
            self.append_token()
            self.token_pos = Pos(self.line, self.col)
            self.state = TokenType.OPERATOR
        elif self.state == TokenType.OPERATOR and char not in OPERATORS and char != Re.SEMICOLON:
            self.append_token()
            self.token_pos = Pos(self.line, self.col)
            self.state = TokenType.KEYWORD

        if char == Re.SEMICOLON:
            if expect_semicolon:
                self.append_token()
                return False
            if not self.allow_semicolon:
                raise JMCSyntaxException(
                    "Unexpected semicolon(;)", None, self)

            self.allow_semicolon = False
            if self.token_str in {"I", "B", "L"}:
                self.token_str += char
                return True

            raise JMCSyntaxException(
                "Unexpected semicolon(;)", None, self)

        self.token_str += char
        return True

    def __parse_newline(self, char: str):
        self.is_comment = False
        if self.state == TokenType.STRING:
            if self.quote == Quote.BACKTICK:
                self.token_str += char
            else:
                raise JMCSyntaxException(
                    "String literal contains an unescaped line break.", None, self, entire_line=True, display_col_length=False)  # suggestion="Consider changing '\\n' to '\\\\n'")
        if self.state == TokenType.COMMENT:
            self.state = None
        elif self.state == TokenType.KEYWORD or self.state == TokenType.OPERATOR:
            self.append_token()
        elif self.state == TokenType.PAREN:
            self.token_str += char
        self.line += 1
        self.col = 0

    def __parse_multiline_string(self):
        lines = self.token_str.split(NEW_LINE)
        if len(lines) <= 2:
            if len(lines) == 1:
                raise JMCSyntaxException(
                    "Expected newline after open backtick(`) for multiline string", None, self, display_col_length=False)
            if len(lines) == 2:
                raise JMCSyntaxException(
                    "Expected newline before close backtick(`) for multiline string", None, self)
        if lines[0] and not re.match(Re.WHITESPACE, lines[0]):
            raise JMCSyntaxException(
                f"Expected whitespaces line after open backtick(`) (got {lines[0]!r})", None, self)
        if lines[-1] and not re.match(Re.WHITESPACE, lines[-1]):
            raise JMCSyntaxException(
                f"Expected whitespaces line before close backtick(`) (got {lines[-1]!r})", None, self)
        self.token_str = "\n".join(lines[1:-1])

    def __parse_string(self, char: str):
        self.token_str += char
        if char == Re.BACKSLASH and not self.is_escaped:
            self.is_escaped = True
        elif char == self.quote and not self.is_escaped:
            if self.quote == Quote.BACKTICK:
                self.token_str: str = literal_eval(
                    '"""\n' + self.token_str[1:-1] + '\n"""')[1:-1]
                self.__parse_multiline_string()
            else:
                self.token_str: str = literal_eval(self.token_str)
            self.append_token()
        elif self.is_escaped:
            self.is_escaped = False

    def __should_terminate_line(self, start_at: int = 0) -> bool:
        return self.keywords[start_at].string in TERMINATE_LINE or (
            self.keywords[start_at].string == "execute" and self.keywords[-2].string in {
                "run", "expand"}
        ) or is_decorator(self.keywords[start_at].string) or (len(self.keywords) >= 3 and self.keywords[-2].string == "run" and self.keywords[-3].string == "return")

    def __is_shorten_if(self) -> bool:
        return self.keywords[0].string == "if" and len(self.keywords) >= 3 and (
            self.keywords[2].string != "expand"
            and
            self.keywords[2].token_type != TokenType.PAREN_CURLY
        )

    def __parse_paren(self, char: str, expect_semicolon: bool) -> bool:
        self.token_str += char
        if self.is_string:
            if char == Re.BACKSLASH and not self.is_escaped:
                self.is_escaped = True
            elif char == self.quote and not self.is_escaped:
                self.is_string = False
            elif self.is_escaped:
                self.is_escaped = False
            return False
        if self.is_comment:
            return False
        if char != Re.SLASH and self.is_slash:
            self.is_slash = False

        if char == self.r_paren and self.paren_count == 0:
            is_paren = False
            if self.paren == Paren.L_CURLY:
                self.state = TokenType.PAREN_CURLY
                is_paren = True
            elif self.paren == Paren.L_ROUND:
                self.state = TokenType.PAREN_ROUND
            elif self.paren == Paren.L_SQUARE:
                self.state = TokenType.PAREN_SQUARE
            self.append_token()
            if is_paren and expect_semicolon and self.__should_terminate_line():
                if self.__is_shorten_if() and not self.__should_terminate_line(start_at=2):
                    return True
                self.append_keywords()
            return True

        if char == self.paren:
            self.paren_count += 1
        elif char == self.r_paren:
            self.paren_count -= 1
        elif char in {Quote.SINGLE, Quote.DOUBLE, Quote.BACKTICK}:
            self.is_string = True
            self.quote = char
        elif char == Re.HASH and not self.keywords:
            self.is_comment = True
        elif char == Re.SLASH:
            if self.is_slash:
                self.is_comment = True
            else:
                self.is_slash = True
        return False

    def __parse_chars(self, string: str, expect_semicolon: bool):
        for char in string:
            self.col += 1
            if char == Re.SEMICOLON and self.state is None and not expect_semicolon:
                raise JMCSyntaxException(
                    "Unexpected semicolon(;)", None, self)

            if char == Re.NEW_LINE:
                self.__parse_newline(char)
                continue

            if char == Re.SLASH and self.is_slash and self.state != TokenType.PAREN and self.state != TokenType.STRING:
                self.token_str = self.token_str[:-1]
                if self.token_str:
                    self.append_token()
                self.state = TokenType.COMMENT
                continue

            if self.state == TokenType.KEYWORD or self.state == TokenType.OPERATOR:
                if self.__parse_keyword_and_operator(char, expect_semicolon):
                    self.is_slash = (char == Re.SLASH)
                    continue

            if self.state is None:
                if self.__parse_none(char):
                    continue

            elif self.state == TokenType.STRING:
                self.__parse_string(char)

            elif self.state == TokenType.PAREN:
                if self.__parse_paren(char, expect_semicolon):
                    continue

            elif self.state == TokenType.COMMENT:
                pass

            self.is_slash = (char == Re.SLASH)

    def parse(self, string: str, line: int, col: int, expect_semicolon: bool,
              allow_last_missing_semicolon: bool = False) -> list[list[Token]]:
        """
        Parse string

        :param string: String to parse
        :param line: Current line
        :param col: Current column
        :param expect_semicolon: Whether to expect a semicolon at the end
        :param allow_last_missing_semicolon: Whether to allow last missing last semicolon, defaults to False
        :raises JMCSyntaxException: Unexpected semicolon
        :raises JMCSyntaxException: String literal contains an unescaped line break
        :raises JMCSyntaxException: Unexpected right bracket (Right brackets > Left brackets)
        :raises JMCSyntaxException: String literal contains an unescaped line break
        :raises JMCSyntaxException: Bracket was never closed (Left brackets > Right brackets)
        :raises JMCSyntaxException: Semicolon missing
        :return: List of keywords(list of tokens)
        """
        self.list_of_keywords = []
        self.line = line
        self.col = col - 1
        self.keywords = []
        self.state = None
        self.token_str = ""
        self.token_pos = None
        # String
        self.quote = None
        self.is_escaped = False
        # Parenthesis
        self.paren = None
        self.r_paren = None
        self.paren_count = 0
        self.is_string = False
        self.is_comment = False  # For paranthesis
        # Comment
        self.is_slash = False

        self.__parse_chars(string, expect_semicolon)

        if self.state == TokenType.STRING:
            raise JMCSyntaxException(
                "String literal contains an unescaped line break", None, self, entire_line=True, display_col_length=False)
        if self.state == TokenType.PAREN:
            if self.token_pos is None:
                raise ValueError("Tokenizer.token_pos is stil None")
            raise JMCSyntaxException(
                "Bracket was never closed", Token(TokenType.KEYWORD, self.token_pos.line, self.token_pos.col, self.paren if self.paren is not None else ''), self, suggestion="This can be the result of unclosed string as well")
        if expect_semicolon and (self.keywords or self.token_str):
            if self.token_str != "":
                self.append_token()
            if allow_last_missing_semicolon:
                self.append_keywords()
            else:
                raise JMCSyntaxException(
                    "Expected semicolon(;)", self.keywords[-1], self, col_length=True)

        if not expect_semicolon:
            if self.token_str != "":
                self.append_token()
            if self.keywords:
                self.append_keywords()

        return self.list_of_keywords

    def split_keyword_token(self, token: Token, split_str: str) -> list[Token]:
        """
        Split a keyword token into multiple tokens

        :param token: A token that will be splitted
        :param split_str: The string for splitting token
        :raises ValueError: non-keyword token used
        :return: List of tokens
        """
        if token.token_type != TokenType.KEYWORD:
            raise ValueError(
                "Called split_token on non-keyword token."
            )
        strings = []
        for string in token.string.split(split_str):
            if string:
                strings.append(string)
            strings.append(split_str)
        strings = strings[:-1]
        tokens: list[Token] = []
        col = token.col
        for string in strings:
            tokens.append(Token(
                TokenType.KEYWORD, token.line, col, string))
            col += len(string)
        return tokens

    def find_token(self, tokens: list[Token],
                   string: str, allow_string_token: bool = False) -> list[list[Token]]:
        """
        Split list of tokens by token that match the string

        :param tokens: List of token
        :param string: String to match for splitting
        :param allow_string_token: Whether to allow string token
        :return: List of list of tokens

        .. example::
        >>> find_token([a,b,c,d], b.string)
        [[a], [c,d]]
        """
        result: list[list[Token]] = []
        token_array: list[Token] = []
        for token in tokens:
            if allow_string_token:
                is_append_result = token.string == string

            else:
                is_append_result = token.string == string and token.token_type != TokenType.STRING

            if is_append_result:
                result.append(token_array)
                token_array = []
            else:
                token_array.append(token)

        result.append(token_array)
        return result

    def merge_tokens(self, tokens: list[Token],
                     use_full_string: bool = False, lexer_to_cleanup: "Lexer | None" = None) -> Token:
        """
        Merge multiple token together

        :param tokens: List of tokens to merge
        :param use_full_string: whether to use fullstring including quatation mark
        :return: A token with the same token type as the first token (Unless it's an operator, then the type will be keyword)
        """
        def __handle_token(token: Token):
            if lexer_to_cleanup is not None and token.token_type in (
                    TokenType.PAREN_CURLY, TokenType.PAREN_ROUND, TokenType.PAREN_SQUARE):
                return lexer_to_cleanup.clean_up_paren_token(token, self)
            if use_full_string:
                return token.get_full_string()
            return token.string

        token_type = tokens[0].token_type
        if token_type == TokenType.OPERATOR:
            token_type = TokenType.KEYWORD
        return Token(token_type, tokens[0].line, tokens[0].col, "".join(
            __handle_token(token) for token in tokens))

    def __parse_func_arg(
            self, tokens: list[Token], is_kwargs: bool, is_nbt: bool = False) -> list[Token]:
        """
        Parse an argument in function arguments (Used in parse_func_args)

        :param tokens: List of tokens
        :param is_kwargs: Boolean of Kwargs to check if it should throw an error
        :param is_nbt: Whether it is an NBT/JSobject (If false, it's a function argument)
        :return: Tokens to be pushed to 'args' or 'kwargs'
        """
        where = "function argument" if is_nbt else "JSObject/NBT"
        if tokens[0].token_type in {TokenType.KEYWORD, TokenType.OPERATOR} and len(
                tokens) != 1:
            return tokens

        if len(tokens) > 1:
            if tokens[0].string == "()" and tokens[1].string == "=>":
                if len(
                        tokens) < 3:
                    raise JMCSyntaxException(
                        "Expected curly bracket after '()=>' (got nothing)", tokens[1], self)
                if tokens[2].token_type != TokenType.PAREN_CURLY:
                    raise JMCSyntaxException(
                        f"Expected curly bracket after '()=>' (got {tokens[2].token_type.value})", tokens[2], self)
                if len(tokens) > 3:
                    raise JMCSyntaxException(
                        "Unexpected token after arrow function '()=>{}'", tokens[3], self)
                token_ = tokens[2]
                return [Token(
                    string=token_.string, line=token_.line, col=token_.col + 1, token_type=TokenType.FUNC)]

            raise JMCSyntaxException(
                f"Unexpected {tokens[1].token_type.value} after {tokens[0].token_type.value} in {where}",
                tokens[1],
                self, suggestion="You may have missed a comma")
        if tokens[0].string == (":" if is_nbt else "="):
            raise JMCSyntaxException(
                f"Empty key in {where}", tokens[0], self)
        if is_kwargs:
            raise JMCSyntaxException(
                "Positional argument follows keyword argument", tokens[0], self, suggestion="Try rearranging arguments")
        return tokens

    def parse_func_args(
            self, token: Token) -> tuple[list[list[Token]], dict[str, list[Token]]]:
        """
        Parse arguments of custom JMC function (Do NOT validate the arguments)

        :param token: paren_round token containing arguments for custom JMC function
        :return: Tuple of arguments(list of list of tokens) and keyword arguments(dictionary of key(string) and list of token)
        """
        if token.token_type != TokenType.PAREN_ROUND:
            raise JMCSyntaxException(
                "Expected (", token, self, display_col_length=False)
        _keywords = self.parse(
            token.string[1:-1], line=token.line, col=token.col + 1, expect_semicolon=False)
        if not _keywords:
            return ([], {})
        keywords = _keywords[0]
        args: list[list[Token]] = []
        kwargs: dict[str, list[Token]] = {}
        comma_separated_tokens = self.find_token(keywords, ",")
        if not comma_separated_tokens[-1]:
            raise JMCSyntaxException(
                "Unexpected comma at the end of function arguments",
                keywords[-1],
                self)
        comma_token_index = 0
        for comma_separated_token in comma_separated_tokens:
            # List of tokens between commas
            if not comma_separated_token:
                raise JMCSyntaxException(
                    "Unexpected comma in function arguments",
                    keywords[comma_token_index],
                    self)
            comma_token_index += len(comma_separated_token) + 1

            if (
                len(comma_separated_token) > 1
                and
                comma_separated_token[1].string in {"=", "=+", "=-"}
            ):
                if len(comma_separated_token) == 2:
                    raise JMCSyntaxException(
                        "Expected keyword argument after '=' in function arguments",
                        comma_separated_token[1],
                        self)
                key = comma_separated_token[0].string
                value = self.__parse_func_arg(
                    comma_separated_token[2:], False)
                equal_token = comma_separated_token[1]
                if (equal_token.string in {"=+", "=-"}):
                    value.insert(
                        0,
                        Token(
                            equal_token.token_type,
                            equal_token.line,
                            equal_token.col +
                            1, equal_token.string[1:], equal_token._macro_length))
                if key in kwargs:
                    raise JMCSyntaxException(
                        f"Duplicated key({key})", comma_separated_token[0], self)
                kwargs[key] = value
                continue

            args.append(
                self.__parse_func_arg(
                    comma_separated_token,
                    bool(kwargs)))

        return args, kwargs

    def parse_param(self, token: Token) -> list[str]:
        """
        Parse user's parameters for lazy function

        :param token: paren_round token containing parameters
        :return: list of parameters in string
        """
        assert token.token_type == TokenType.PAREN_ROUND

        if token.string == "()":
            return []

        keywords = self.parse(token.string[1:-
                                           1], line=token.line, col=token.col +
                              1, expect_semicolon=False)[0]
        is_expect_comma = False  # Whether to expect comma token
        params: list[str] = []

        for token_ in keywords:
            if token_.token_type == TokenType.COMMA:
                if not is_expect_comma:
                    raise JMCSyntaxException(
                        "Unexpected duplicated comma(,)", token_, self)
                is_expect_comma = False
                continue

            if is_expect_comma:
                raise JMCSyntaxException(
                    "Expect comma(,)", token_, self)

            if token_.token_type != TokenType.KEYWORD:
                raise JMCSyntaxException(
                    f"Expected keyword in parameters (got {token_.token_type.value})", token_, self)
            params.append(token_.string)
            is_expect_comma = True

        return params

    def parse_list(self, token: Token) -> list[Token]:
        """
        Parse list

        :param token: paren_square token containing list
        :return: Dictionary of key(string) and Token
        """
        if token.token_type != TokenType.PAREN_SQUARE:
            raise JMCSyntaxException(
                "Expected list/array", token, self, suggestion="Expected [")

        if token.string == "[]":
            return []

        keywords = self.parse(token.string[1:-
                                           1], line=token.line, col=token.col +
                              1, expect_semicolon=False)[0]
        is_expect_comma = False  # Whether to expect comma token
        tokens: list[Token] = []

        for token_ in keywords:
            if token_.token_type == TokenType.COMMA:
                if not is_expect_comma:
                    raise JMCSyntaxException(
                        "Unexpected duplicated comma(,)", token_, self)
                is_expect_comma = False
                continue

            if is_expect_comma:
                raise JMCSyntaxException(
                    "Expect comma(,)", token_, self)
            tokens.append(token_)
            is_expect_comma = True

        return tokens

    # def parse_nbt(self, token: Token) -> dict[str, str]:
    #     return {}

    def parse_js_obj(self, token: Token) -> dict[str, Token]:
        """
        Parse JavaScript Object (Not JSON)

        :param token: paren_curly token containing JS object
        :return: Dictionary of key(string) and Token
        """
        if token.token_type != TokenType.PAREN_CURLY:
            raise JMCSyntaxException(
                "Expected JavaScript Object", token, self, suggestion="Expected {")
        _keywords = self.parse(
            token.string[1:-1], line=token.line, col=token.col + 1, expect_semicolon=False)
        if not _keywords:
            return {}
        keywords = _keywords[0]
        js_obj: dict[str, Token] = {}
        comma_separated_tokens = self.find_token(keywords, ",")
        if not comma_separated_tokens[-1]:
            raise JMCSyntaxException(
                "Unexpected comma at the end of JSObject/NBT",
                keywords[-1],
                self)
        comma_token_index = 0
        for comma_separated_token in comma_separated_tokens:
            # List of tokens between commas
            if not comma_separated_token:
                raise JMCSyntaxException(
                    "Unexpected comma in JSObject/NBT",
                    keywords[comma_token_index],
                    self)
            comma_token_index += len(comma_separated_token) + 1

            if len(
                    comma_separated_token) == 1 or comma_separated_token[1].string != ":":
                raise JMCSyntaxException(
                    "Expected 'key:value' in JSObject/NBT", comma_separated_token[0], self)

            if len(comma_separated_token) == 2:
                raise JMCSyntaxException(
                    "Expected value after ':' in JSObject/NBT",
                    comma_separated_token[1],
                    self)
            key = comma_separated_token[0].string
            value = self.__parse_func_arg(
                comma_separated_token[2:], False, is_nbt=True)
            if key in js_obj:
                raise JMCSyntaxException(
                    f"Duplicated key({key})", comma_separated_token[0], self)
            js_obj[key] = self.merge_tokens(value)
            continue

        return js_obj
