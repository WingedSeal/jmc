
from enum import Enum, auto
import re
from typing import TYPE_CHECKING

from ..utils import is_float, is_number
from ..exception import JMCSyntaxException
from ..datapack import DataPack
from ..tokenizer import Token, TokenType, Tokenizer

if TYPE_CHECKING:
    from ..lexer_func_content import FuncContent


class NBTType(Enum):
    AUTO_STORAGE = auto()
    STORAGE = auto()
    BLOCK = auto()
    ENTITY = auto()


def get_nbt_string(nbt_type: "NBTType") -> str:
    return {
        NBTType.AUTO_STORAGE: "storage",
        NBTType.STORAGE: "storage",
        NBTType.BLOCK: "block",
        NBTType.ENTITY: "entity"
    }[nbt_type]


def get_nbt_type(tokens: list[Token]) -> NBTType | None:
    if len(tokens) < 2:
        return None
    __is_storage_nbt = len(tokens) > 3 and tokens[0].token_type == TokenType.KEYWORD and tokens[
        1].string == ":" and tokens[2].token_type == TokenType.KEYWORD and tokens[3].string == "::"
    __is_auto_storage_nbt = tokens[0].token_type == TokenType.KEYWORD and tokens[1].string == "::"
    __is_full_auto_storage_nbt = tokens[0].string == "::"
    __is_block_nbt = tokens[0].token_type == TokenType.PAREN_SQUARE and tokens[1].string == "::"
    __is_entity_nbt = tokens[0].string.startswith(
        "@") and tokens[0].string[1] in "parse" and (tokens[1].string == "::" or (tokens[1].token_type == TokenType.PAREN_SQUARE and tokens[2].string == "::"))
    if __is_entity_nbt:
        return NBTType.ENTITY
    elif __is_storage_nbt:
        return NBTType.STORAGE
    elif __is_auto_storage_nbt:
        return NBTType.AUTO_STORAGE
    elif __is_full_auto_storage_nbt:
        return NBTType.AUTO_STORAGE
    elif __is_block_nbt:
        return NBTType.BLOCK
    else:
        return None


def merge_path(tokens: list[Token], start_index: int,
               tokenizer: Tokenizer, datapack: DataPack) -> str:
    """
    Merge tokens into an NBT path and delete it from the list

    :param tokens: Tokens
    :return: NBT Path string
    """
    if len(tokens) <= start_index:
        return ""
    if tokens[start_index].token_type not in (TokenType.KEYWORD, TokenType.PAREN_CURLY) or tokens[start_index].string.startswith(
            "^"):
        return ""
    if tokens[start_index].token_type == TokenType.PAREN_CURLY:
        string = datapack.lexer.clean_up_paren_token(
            tokens[start_index], tokenizer)
    else:
        string = tokens[start_index].string
    del tokens[start_index]

    if len(tokens) <= start_index:
        return string

    for index, token in enumerate(tokens[start_index:]):
        if token.string.startswith("."):
            string += token.string
        elif (
            token.token_type == TokenType.PAREN_CURLY
            or
            (token.token_type == TokenType.PAREN_SQUARE and not re.match(
                r"-?\d+:-?\d*", token.string[1:-1]))
            or
            (token.token_type == TokenType.PAREN_ROUND and string.endswith("$"))
        ):
            string += datapack.lexer.clean_up_paren_token(token, tokenizer)
        else:
            del tokens[start_index:start_index + index]
            return string
    del tokens[start_index:start_index + index + 1]
    return string


def extract_nbt(tokens: list[Token], tokenizer: Tokenizer,
                datapack: DataPack, nbt_type: NBTType, start_index: int = 0) -> tuple[str, str, str]:
    """
    Extract nbt from tokens and delete it

    :param tokens: List of tokens
    :param tokenizer: Tokenizer
    :param datapack: Datapack
    :param nbt_type: NBT type
    :param start_index: Index of the first token(keyword) in jmc nbt syntax defaults to 0
    :return: Tuple of [block|storage|entity, target, path]
    """
    if nbt_type == NBTType.AUTO_STORAGE:
        if tokens[start_index].string == "::":
            path = merge_path(
                tokens, start_index + 1, tokenizer, datapack)
            del tokens[start_index:start_index + 1]
            return get_nbt_string(nbt_type), datapack.namespace + \
                ":" + datapack.namespace, " " + path if path else ""
        else:
            target = tokens[start_index].string
            path = merge_path(
                tokens, start_index + 2, tokenizer, datapack)
            del tokens[start_index:start_index + 2]
            return get_nbt_string(nbt_type), datapack.namespace + \
                ":" + target, " " + path if path else ""
    elif nbt_type == NBTType.STORAGE:
        target = tokens[start_index].string + tokens[start_index +
                                                     1].string + tokens[start_index + 2].string
        path = merge_path(
            tokens, start_index + 4, tokenizer, datapack)
        del tokens[start_index:start_index + 4]
        return get_nbt_string(nbt_type), target, " " + path if path else ""
    elif nbt_type == NBTType.BLOCK:
        target = " ".join(
            _token.string for _token in tokenizer.parse_list(
                tokens[start_index]))
        path = merge_path(
            tokens, start_index + 2, tokenizer, datapack)
        del tokens[start_index:start_index + 2]
        return get_nbt_string(nbt_type), target, " " + path if path else ""
    elif nbt_type == NBTType.ENTITY:
        if tokens[1].token_type == TokenType.PAREN_SQUARE:
            target = tokens[start_index].string + \
                datapack.lexer.clean_up_paren_token(
                    tokens[start_index + 1], tokenizer)
            path = merge_path(
                tokens, start_index + 3, tokenizer, datapack)
            del tokens[start_index:start_index + 3]
        else:
            target = tokens[start_index].string
            path = merge_path(
                tokens, start_index + 2, tokenizer, datapack)
            del tokens[start_index:start_index + 2]
        return get_nbt_string(nbt_type), target, " " + path if path else ""
    raise NotImplementedError("Invalid nbt_type")


def __str_slice(token: Token, tokenizer: Tokenizer) -> str:
    slices = token.string[1:-1].split(":")
    if not slices or len(slices) > 2:
        raise JMCSyntaxException(
            "Expected operator after nbt", token, tokenizer)
    if not slices[1]:
        return slices[0].strip()
    return slices[0].strip() + " " + slices[1].strip()


def __get_type_scale(tokens: list[Token],
                     tokenizer: Tokenizer, datapack: DataPack) -> tuple[str, str]:
    type_ = "int"
    scale = "1"
    if len(
            tokens) > 1 and tokens[0].string == "$" and tokens[1].token_type == TokenType.PAREN_ROUND:
        tokens[0] = tokenizer.merge_tokens(
            tokens[0:2], lexer_to_cleanup=datapack.lexer)
        del tokens[1]
    if len(tokens) > 1 and (is_float(tokens[0].string) or tokens[0].string.startswith(
            "$")) and tokens[1].string == "*":
        scale = tokens[0].string
        del tokens[:2]
    if tokens[0].token_type == TokenType.PAREN_ROUND:
        type_ = tokens[0].string[1:-1].strip()
        if type_ not in ("byte", "short", "int", "long", "float",
                         "double") and not type_.startswith("$"):
            raise JMCSyntaxException(
                f"Unexpected data type ({type_})", tokens[0], tokenizer, suggestion="Available data types are 'bytes', 'short', 'int', 'long', 'float', 'double'")
        del tokens[0]
    return type_, scale


def __clean_token(token: Token, tokenizer: Tokenizer,
                  datapack: DataPack) -> str:
    if token.token_type in (TokenType.PAREN_CURLY,
                            TokenType.PAREN_ROUND, TokenType.PAREN_SQUARE):
        return datapack.lexer.clean_up_paren_token(
            token, tokenizer, is_nbt=True)
    return token.get_full_string()


def nbt_operation(
        tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack, nbt_type: NBTType, FuncContent: type["FuncContent"], prefix: str) -> str:
    left_nbt = tokens[0]
    nbt_type_str, target, path = extract_nbt(
        tokens, tokenizer, datapack, nbt_type)
    if not tokens:
        return f"data get {nbt_type_str} {target}{path}"

    if tokens[0].token_type == TokenType.PAREN_ROUND and tokens[0].string == "()" and path.endswith(
            ".del"):
        return f"data remove {nbt_type_str} {target}{path[:-4]}"

    if tokens[0].string.startswith("^"):
        index = tokens[0].string[1:]
        if len(tokens) > 2 and tokens[1].string == "-":
            tokens[1] = tokenizer.merge_tokens(tokens[1:3])
            del tokens[2]
        if not index:
            index = tokens[1].string
            del tokens[1]
        if not is_number(index):
            raise JMCSyntaxException(
                f"Expect a number after `^` for NBT insert, got {tokens[1].string}", tokens[0], tokenizer)

        del tokens[0]
        if not path:
            raise JMCSyntaxException(
                f"NBT insert cannot be used with root nbt", left_nbt, tokenizer, suggestion="Put something after `::`")
        right_nbt_type = get_nbt_type(tokens)
        if right_nbt_type is None:
            if len(tokens) > 1:
                raise JMCSyntaxException(
                    f"Unexpected token ({tokens[1]})", tokens[1], tokenizer)
            return f"data modify {nbt_type_str} {target}{path} insert {index} value {__clean_token(tokens[0], tokenizer, datapack)}"
        else:
            right_nbt_type_str, right_target, right_path = extract_nbt(
                tokens, tokenizer, datapack, right_nbt_type)
            if tokens:
                if tokens[0].token_type != TokenType.PAREN_SQUARE:
                    raise JMCSyntaxException(
                        f"Unexpected token ({tokens[0]})", tokens[0], tokenizer)
                return f"""data modify {nbt_type_str} {target}{path} insert {index} string {right_nbt_type_str} {right_target}{right_path} {
                            __str_slice(tokens[0], tokenizer)}"""
            else:
                return f"data modify {nbt_type_str} {target}{path} insert {index} from {right_nbt_type_str} {right_target}{right_path}"

    if tokens[0].token_type != TokenType.OPERATOR:
        raise JMCSyntaxException(
            f"Expected operator after nbt (got {tokens[0].token_type.value})", tokens[0], tokenizer)

    operator_token = tokens[0]
    operator = tokens[0].string
    if not tokens:
        raise JMCSyntaxException(
            f"Expected a token after {operator}", tokens[0], tokenizer)
    del tokens[0]

    if operator in ("<<", ">>", "="):
        right_nbt_type = get_nbt_type(tokens)
        __is_command = tokens[0].token_type == TokenType.KEYWORD and not is_float(
            tokens[0].string) and not is_float(
            tokens[0].string[:-1]) and tokens[0].string not in ("true", "false") and tokens[0].string != "$"

        if operator == "=" and right_nbt_type is None and (
            __is_command  # = <command>
            or
            # = <scale> * <command> / = <scale> * (<type>) <command>
                (tokens[0].token_type == TokenType.KEYWORD and is_float(
                tokens[0].string) and len(
                tokens) > 1 and tokens[1].string == "*")
            or
            # = $(scale) * <command>
                (tokens[0].string == "$" and len(
                tokens) > 2 and tokens[1].token_type == TokenType.PAREN_ROUND
                and tokens[2].string == "*")
            or
            # = (<type>) <command>
            tokens[0].token_type == TokenType.PAREN_ROUND
        ):
            type_, scale = __get_type_scale(tokens, tokenizer, datapack)
            func = FuncContent(tokenizer,
                               [tokens],
                               is_load=False,
                               lexer=datapack.lexer,
                               prefix=prefix).parse()
            if len(func) > 1:
                raise JMCSyntaxException(
                    f"Multiple commands (got {len(func)}) cannot be assigned to nbt", tokens[0], tokenizer)
            return f"""execute store result {nbt_type_str} {target}{path} {type_} {scale} run {func[0]}"""
        full_operator = {
            "<<": "append",
            ">>": "prepend",
            "=": "set"
        }[operator]
        if not path:
            raise JMCSyntaxException(
                f"NBT {full_operator} cannot be used with root nbt", left_nbt, tokenizer, suggestion="Put something after `::`")
        if right_nbt_type is None:
            if tokens[0].string == "-":
                tokens = [tokenizer.merge_tokens(tokens)]

            if len(tokens) > 1:
                raise JMCSyntaxException(
                    f"Unexpected token ({tokens[1]})", tokens[1], tokenizer)
            return f"data modify {nbt_type_str} {target}{path} {full_operator} value {__clean_token(tokens[0], tokenizer, datapack)}"
        else:
            right_nbt_type_str, right_target, right_path = extract_nbt(
                tokens, tokenizer, datapack, right_nbt_type)
            if tokens:
                if tokens[0].token_type != TokenType.PAREN_SQUARE:
                    raise JMCSyntaxException(
                        f"Unexpected token ({tokens[0].string})", tokens[0], tokenizer)
                return f"""data modify {nbt_type_str} {target}{path} {full_operator} string {right_nbt_type_str} {right_target}{right_path} {
                            __str_slice(tokens[0], tokenizer)}"""
            else:
                return f"data modify {nbt_type_str} {target}{path} {full_operator} from {right_nbt_type_str} {right_target}{right_path}"

    elif operator == "+=":
        right_nbt_type = get_nbt_type(tokens)
        if right_nbt_type is None:
            if len(tokens) > 1:
                raise JMCSyntaxException(
                    f"Unexpected token ({tokens[1].string})", tokens[1], tokenizer)
            if not path:
                return f"data merge {nbt_type_str} {target} {__clean_token(tokens[0], tokenizer, datapack)}"
            return f"data modify {nbt_type_str} {target}{path} merge value {__clean_token(tokens[0], tokenizer, datapack)}"
        else:
            if not path:
                raise JMCSyntaxException(
                    f"NBT merge with another nbt cannot be used with root nbt", left_nbt, tokenizer,
                    suggestion="Put something after `::` or merge with literal value instead")
            right_nbt_type_str, right_target, right_path = extract_nbt(
                tokens, tokenizer, datapack, right_nbt_type)
            if tokens:
                if tokens[0].token_type != TokenType.PAREN_SQUARE:
                    raise JMCSyntaxException(
                        f"Unexpected token ({tokens[0]})", tokens[0], tokenizer)
                return f"""data modify {nbt_type_str} {target}{path} merge string {right_nbt_type_str} {right_target}{right_path} {
                            __str_slice(tokens[0], tokenizer)}"""
            else:
                return f"data modify {nbt_type_str} {target}{path} merge from {right_nbt_type_str} {right_target}{right_path}"

    elif operator == "?=":
        type_, scale = __get_type_scale(tokens, tokenizer, datapack)
        if len(tokens) == 0:
            raise JMCSyntaxException(
                f"Expected command after operator{tokens[0].string} (got nothing)", tokens[1], tokenizer)
        func_content = FuncContent(tokenizer, [tokens],
                                   is_load=False, lexer=datapack.lexer, prefix=prefix).parse()
        if len(func_content) > 1:
            raise JMCSyntaxException(
                "Operator '?=' does not support command that return multiple commands", tokens[2], tokenizer)
        if func_content[0].startswith("execute"):
            # len("execute ") = 8
            return f"execute store success {nbt_type_str} {target}{path} {type_} {scale} {func_content[0][8:]}"
        return f"execute store success {nbt_type_str} {target}{path} {type_} {scale} run {func_content[0]}"

    elif operator == "*":
        return f"data get {nbt_type_str} {target}{path} {tokens[0].string}"

    raise JMCSyntaxException(
        f"Unrecognized operator ({operator})", operator_token, tokenizer)
