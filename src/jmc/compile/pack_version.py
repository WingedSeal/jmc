from .exception import MinecraftVersionTooLow

from .tokenizer import Token, Tokenizer


class PackVersion:
    """
    Class containing information about pack_format
    """
    __slot__ = ('_pack_format', )

    def __init__(self, pack_format: int) -> None:
        self._pack_format = pack_format
        """Datapack's pack_format"""

    def requires(self, pack_format: int, token: Token,
                 tokenizer: Tokenizer, suggestion: str | None = None) -> None:
        if self._pack_format < pack_format:
            raise MinecraftVersionTooLow(
                pack_format, token, tokenizer, suggestion=suggestion)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, int):
            return self._pack_format == __value
        elif isinstance(__value, type(self)):
            return self._pack_format == __value._pack_format
        return False

    def __ne__(self, __value: object) -> bool:
        return not self == __value

    def __hash__(self) -> int:
        return hash(self._pack_format)

    def __gt__(self, __value: object) -> bool:
        if isinstance(__value, int):
            return self._pack_format > __value
        elif isinstance(__value, type(self)):
            return self._pack_format > __value._pack_format
        return False

    def __ge__(self, __value: object) -> bool:
        if isinstance(__value, int):
            return self._pack_format >= __value
        elif isinstance(__value, type(self)):
            return self._pack_format >= __value._pack_format
        return False

    def __lt__(self, __value: object) -> bool:
        if isinstance(__value, int):
            return self._pack_format < __value
        elif isinstance(__value, type(self)):
            return self._pack_format < __value._pack_format
        return False

    def __le__(self, __value: object) -> bool:
        if isinstance(__value, int):
            return self._pack_format <= __value
        elif isinstance(__value, type(self)):
            return self._pack_format <= __value._pack_format
        return False
