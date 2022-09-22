from .exception import HeaderDuplicatedMacro, HeaderSyntaxException
from .log import Logger

logger = Logger(__name__)

class Header:
    macros: dict[str, str] = {}

def parse_header(header_str: str, file_name: str) -> Header:
    header = Header()
    lines = header_str.split("\n")
    for line, line_str in enumerate(lines):
        line += 1
        if line_str.isspace() or line_str.startswith("//"):
            continue

        if not line_str.startswith("#"):
            raise HeaderSyntaxException(f"In {file_name}\nExpected '#' at line {line} col 1\n{line_str}")

        directive = line_str[1:]
        args = directive.split()

        if args[0] == "define":
            if len(args) == 3:
                key = args[1]
                value = args[2]
                logger.debug(f'Define "{key}" as "{value}"')
                if key in header.macros:
                    raise HeaderDuplicatedMacro(f"In {file_name}\n'{key}' macro is already defined at line {line}\n{line_str}")
                header.macros[key] = value

            else:
                HeaderSyntaxException(f"In {file_name}\n'define' takes 2 arguments (got {len(args)-1}) at line {line}\n{line_str}")
        else:
            raise HeaderSyntaxException(f"In {file_name}\nUnrecognized directive '{args[0]}' at line {line} col 1\n{line_str}")
        

