
from enum import Enum, auto

from ..datapack import DataPack
from ..tokenizer import Token, TokenType, Tokenizer


class NBTType(Enum):
    AUTO_STORAGE = "storage"
    STORAGE = "storage"
    BLOCK = "block"
    ENTITY = "entity"


def get_nbt_type(tokens: list[Token]) -> NBTType | None:
    if len(tokens) < 2:
        return None
    __is_storage_nbt = len(tokens) > 3 and tokens[0].token_type == TokenType.KEYWORD and tokens[
        1].string == ":" and tokens[2].token_type == TokenType.KEYWORD and tokens[3].string == "::"
    __is_auto_storage_nbt = tokens[0].token_type == TokenType.KEYWORD and tokens[1].string == "::"
    __is_block_nbt = tokens[0].token_type == TokenType.PAREN_SQUARE and tokens[1].string == "::"
    __is_entity_nbt = tokens[0].string.startswith(
        "@") and tokens[0].string[1] in "parse" and (tokens[1].string == "::" or (tokens[1].token_type == TokenType.PAREN_SQUARE and tokens[2].string == "::"))
    if __is_entity_nbt:
        return NBTType.ENTITY
    elif __is_auto_storage_nbt:
        return NBTType.AUTO_STORAGE
    elif __is_storage_nbt:
        return NBTType.STORAGE
    elif __is_block_nbt:
        return NBTType.BLOCK
    else:
        return None


def merge_path(tokens: list[Token]) -> tuple[str, int]:
    # todo
    if not tokens:
        return "", 0
    return tokens[0].string, 1


def extract_nbt(tokens: list[Token], tokenizer: Tokenizer,
                datapack: DataPack, nbt_type: NBTType, start_index: int = 0) -> tuple[str, str, str]:
    """
    Merge objective:selector[] into one token

    :param tokens: List of tokens
    :param tokenizer: Tokenizer
    :param datapack: Datapack
    :param nbt_type: NBT type
    :param start_index: Index of the first token(keyword) in jmc nbt syntax defaults to 0
    :return: Tuple of [block|storage|entity, target, path]
    """
    if nbt_type == NBTType.AUTO_STORAGE:
        target = tokens[start_index].string
        path, length = merge_path(tokens[start_index + 2:])
        del tokens[start_index:length + 2]
        return nbt_type.value, datapack.namespace + ":" + target, path
    elif nbt_type == NBTType.STORAGE:
        target = tokens[start_index].string + tokens[start_index +
                                                     1].string + tokens[start_index + 2].string
        path, length = merge_path(tokens[start_index + 4:])
        del tokens[start_index:length + 4]
        return nbt_type.value, target, path
    elif nbt_type == NBTType.BLOCK:
        target = " ".join(
            _token.string for _token in tokenizer.parse_list(
                tokens[start_index]))
        path, length = merge_path(tokens[start_index + 2:])
        del tokens[start_index:length + 2]
        return nbt_type.value, target, path
    elif nbt_type == NBTType.ENTITY:
        if tokens[1].token_type == TokenType.PAREN_SQUARE:
            target = tokens[start_index].string + \
                tokens[start_index + 1].string
            path, length = merge_path(tokens[start_index + 3:])
            del tokens[start_index:length + 3]
        else:
            target = tokens[start_index].string
            path, length = merge_path(tokens[start_index + 2:])
            del tokens[start_index:length + 2]
        return nbt_type.value, target, path


def nbt_operation(
        tokens: list[Token], tokenizer: Tokenizer, datapack: DataPack, nbt_type: NBTType) -> str:
    nbt_type_str, target, path = extract_nbt(
        tokens, tokenizer, datapack, nbt_type)
    if path:
        path = " " + path
    if not tokens:
        return f"data get {nbt_type_str} {target}{path}"
    return "WIP"
