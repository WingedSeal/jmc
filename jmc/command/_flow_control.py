from typing import Optional
from ..tokenizer import Token, Tokenizer, TokenType
from ..datapack import DataPack
from ..exception import JMCSyntaxException

NEW_LINE = '\n'


def if_(command: list["Token"], datapack: "DataPack", tokenizer: "Tokenizer") -> None:
    if len(command) < 2:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected ( at line {command[0].line} col {command[0].col+command[0].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
        )
    if command[1].token_type != TokenType.paren_round:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected ( at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1]} <-"
        )
    if len(command) < 3:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected {'{'} at line {command[1].line} col {command[1].col+command[1].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col+command[1].length-1]} <-"
        )
    if command[2].token_type != TokenType.paren_curly:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected {'{'} at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1]} <-"
        )

    datapack.lexer.if_else_box.append((command[1], command[2]))


def else_(command: list["Token"], datapack: "DataPack", tokenizer: "Tokenizer") -> Optional[str]:
    if not datapack.lexer.if_else_box:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\n'else' cannot be used without 'if' at line {command[0].line} col {command[0].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length - 1]} <-"
        )

    if len(command) < 2:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpect 'if' or {'{'} at line {command[0].line} col {command[0].col+command[0].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col + command[0].length - 1]} <-"
        )

    if command[1].token_type == TokenType.keyword and command[1].string == 'if':
        if len(command) < 3:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected ( at line {command[1].line} col {command[1].col+command[1].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col+command[1].length-1]} <-"
            )
        if command[2].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected ( at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1]} <-"
            )
        if len(command) < 4:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[2].line} col {command[2].col+command[2].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col+command[2].length-1]} <-"
            )
        if command[3].token_type != TokenType.paren_curly:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[3].line} col {command[3].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[3].line-1][:command[3].col-1]} <-"
            )

        datapack.lexer.if_else_box.append(
            (command[2], command[3]))
    elif command[1].token_type == TokenType.paren_curly:
        datapack.lexer.if_else_box.append(
            (None, command[1])
        )
        return datapack.lexer.parse_if_else(tokenizer)
    else:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpect 'if' or {'{'} at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col]} <-"
        )


def while_(command: list["Token"], datapack: "DataPack", tokenizer: "Tokenizer") -> str:
    if datapack.lexer.do_while_box is None:
        if len(command) < 2:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected ( at line {command[0].line} col {command[0].col+command[0].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
            )
        if command[1].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected ( at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1]} <-"
            )
        if len(command) < 3:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[1].line} col {command[1].col+command[1].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col+command[1].length-1]} <-"
            )
        if command[1].token_type != TokenType.paren_round:
            raise JMCSyntaxException(
                f"In {tokenizer.file_path}\nExpected {'{'} at line {command[2].line} col {command[2].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[2].line-1][:command[2].col-1]} <-"
            )
        return "WHILE NOT IMPLEMENT"
        # TODO: HANDLE WHILE
    else:
        # TODO: HANDLE DO WHILE
        datapack.lexer.do_while_box = None
        return "WHILE NOT IMPLEMENT (found `do`)"


def do(command: list["Token"], datapack: "DataPack", tokenizer: "Tokenizer") -> None:
    if len(command) < 2:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected {'{'} at line {command[0].line} col {command[0].col+command[0].length}.\n{tokenizer.file_string.split(NEW_LINE)[command[0].line-1][:command[0].col+command[0].length-1]} <-"
        )
    if command[1].token_type != TokenType.paren_curly:
        raise JMCSyntaxException(
            f"In {tokenizer.file_path}\nExpected {'{'} at line {command[1].line} col {command[1].col}.\n{tokenizer.file_string.split(NEW_LINE)[command[1].line-1][:command[1].col-1]} <-"
        )
    datapack.lexer.do_while_box = command[1]


def switch(command: list["Token"], datapack: "DataPack", tokenizer: "Tokenizer") -> str:
    return "switch"+str(command)


def for_(command: list["Token"], datapack: "DataPack", tokenizer: "Tokenizer") -> str:
    return "for_"+str(command)
