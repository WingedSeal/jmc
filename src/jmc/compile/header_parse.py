from pathlib import Path
from .header import Header
from .tokenizer import TokenType, Tokenizer
from .exception import HeaderDuplicatedMacro, HeaderFileNotFoundError, HeaderSyntaxException, JMCFileNotFoundError
from .log import Logger

logger = Logger(__name__)


def __parse_header(header_str: str, file_name: str,
                   parent_target: Path, namespace_path: Path) -> Header:
    header = Header()
    lines = header_str.split("\n")
    for line, line_str in enumerate(lines):
        line += 1
        if line_str.isspace() or line_str.startswith("//") or line_str == "":
            continue

        if not line_str.startswith("#"):
            raise HeaderSyntaxException(
                "Expected '#' at the start of the line", file_name, line, line_str)

        if line_str == "#":
            raise HeaderSyntaxException(
                "Expected directive after '#'", file_name, line, line_str)

        directive_and_args = Tokenizer(
            line_str[1:], file_name, line, expect_semicolon=False).programs[0]
        directive_token = directive_and_args[0]
        arg_tokens = directive_and_args[1:]
        if directive_token.token_type != TokenType.KEYWORD:
            raise HeaderSyntaxException(
                f"Expected directive(keyword) after '#' (got {directive_token.token_type})", file_name, line, line_str)

        # #define
        if directive_token.string == "define":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    "Expected keyword after '#define'", file_name, line, line_str)
            key = arg_tokens[0].string
            value = " ".join(token_.string for token_ in arg_tokens[1:])
            logger.debug(f'Define "{key}" as "{value}"')
            if key in header.macros:
                raise HeaderDuplicatedMacro(
                    f"'{key}' macro is already defined", file_name, line, line_str)
            header.macros[key] = value
        # #include
        elif directive_token.string == "include":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.STRING:
                raise HeaderSyntaxException(
                    "Expected included file name(string) after '#include'", file_name, line, line_str)
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#include' (got {len(arg_tokens)})", file_name, line, line_str)
            new_file_name = arg_tokens[0].string
            if not new_file_name.endswith(".hjmc"):
                new_file_name += ".hjmc"
            header_file = parent_target / new_file_name
            if not header_file.is_file():
                raise HeaderFileNotFoundError(header_file)
            with header_file.open('r') as file:
                header_str = file.read()
            logger.info(f"Parsing {header_file}")
            if header.is_header_exist(header_file):
                raise HeaderSyntaxException(
                    f"File {header_file.as_posix()} is already included.", file_name, line, line_str)
            header.add_file_read(header_file)
            __parse_header(
                header_str,
                header_file.as_posix(),
                parent_target,
                namespace_path)

        # #credit
        elif directive_token.string == "credit":
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 0-1 arguments after '#credit' (got {len(arg_tokens)})", file_name, line, line_str)
            if arg_tokens:
                if arg_tokens[0].token_type != TokenType.STRING:
                    raise HeaderSyntaxException(
                        "Expected included file name(string) after '#include'", file_name, line, line_str)
                header.credits.append(arg_tokens[0].string)
            else:
                header.credits.append("")

        # #override_minecraft
        elif directive_token.string == "override_minecraft":
            if arg_tokens:
                raise HeaderSyntaxException(
                    f"Expected 0 arguments after '#override_minecraft' (got {len(arg_tokens)})", file_name, line, line_str)
            header.is_override_minecraft = True

        # #command
        elif directive_token.string == "command":
            if not arg_tokens or len(arg_tokens) != 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#command' (got {len(arg_tokens)})", file_name, line, line_str)
            if arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    f"Expected keyword after '#command' (got {arg_tokens[0].token_type})", file_name, line, line_str)
            header.commands.add(arg_tokens[0].string)

        # #static
        elif directive_token.string == "static":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.STRING:
                raise HeaderSyntaxException(
                    "Expected static folder name(string) after '#static'", file_name, line, line_str)
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#static' (got {len(arg_tokens)})", file_name, line, line_str)
            static_folder = namespace_path / arg_tokens[0].string
            if not static_folder.is_dir():
                # raise JMCFileNotFoundError(
                # f"Static folder not found: {static_folder.as_posix()}\nPlease
                # recheck that the path is correct so that JMC won't
                # accidentally delete your folder.")
                raise HeaderSyntaxException(
                    f"Static folder not found: {static_folder.as_posix()}", file_name, line, line_str, suggestion="Please recheck that the path is correct so that JMC won't accidentally delete your folder.")
            header.statics.add(static_folder)
        else:
            raise HeaderSyntaxException(
                f"Unrecognized directive '{directive_token.string}'", file_name, line, line_str)

    return header


def parse_header(header_str: str, file_name: str,
                 parent_target: Path, namespace_path: Path) -> Header:
    """
    Parse header and store the information in the header object

    :param header_str: String that was read from the file
    :param file_name: Header file's name
    :param parent_target: Path to parent of the main jmc file
    :raises HeaderSyntaxException: A line in the file doesn't start with '#'
    :raises HeaderDuplicatedMacro: Define same macro twice
    :raises HeaderSyntaxException: Too many/little argument for define
    :raises HeaderSyntaxException: File name isn't wrapped in quote or angle bracket (For `#include`)
    :raises HeaderFileNotFoundError: Can't find header file
    :raises HeaderSyntaxException: Include same file twice
    :raises HeaderSyntaxException: Whitespace found in header file's name
    :raises NotImplementedError: WORKING ON `#replace`
    :raises NotImplementedError: WORKING ON `#credit`
    :raises HeaderSyntaxException: Directive (`#something`) is unrecognized
    :return: Header singleton object

    .. TODO::
        implement replace and credit

    """
    header = Header()
    header.is_enable_macro = False
    return_value = __parse_header(
        header_str,
        file_name,
        parent_target,
        namespace_path)
    header.is_enable_macro = True
    return return_value
