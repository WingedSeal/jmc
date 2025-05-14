from .exception import MinecraftVersionTooLow, MinecraftVersionTooHigh

from .tokenizer import Token, Tokenizer


class PackVersion:
    """
    Class containing information about pack_format

    .. example::
    >>> self.datapack.version >= 10
    True
    >>> self.datapack.version > 20
    False
    >>> self.datapack.version.require(7, token, tokenizer)
    None
    >>> self.datapack.version.require(11, token, tokenizer)
    raise MinecraftVersionTooLow
    """
    __slot__ = ('_pack_format', )

    def __init__(self, pack_format: int) -> None:
        self._pack_format = pack_format
        """Datapack's pack_format"""

    def require(self, pack_format: "int | PackVersion", token: Token,
                tokenizer: Tokenizer, suggestion: str | None = None, is_lower: bool = False) -> None:
        """
        Raise MinecraftVersionTooLow when pack_format is too low
        Raise MinecraftVersionTooHigh when pack_format is too high

        :param pack_format: required pack_format
        :param token: Token to raise error
        :param tokenizer: token's Tokenizer
        :param suggestion: error suggestion, defaults to None
        :param is_lower: Set to True when expecting pack_format lower than this
        """
        if isinstance(pack_format, PackVersion):
            pack_format = pack_format._pack_format
        if is_lower:
            if self._pack_format != -1 and self._pack_format >= pack_format:
                raise MinecraftVersionTooHigh(
                    pack_format, token, tokenizer, suggestion=suggestion)
        else:
            if self._pack_format != -1 and self._pack_format < pack_format:
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


class PackVersionFeature:
    VANILLA_MACRO = PackVersion(16)
    """Add Vanilla Macro ('with')"""
    PLS_RENAME_19 = PackVersion(19)
    """TODO: RENAME"""
    PLS_RENAME_21 = PackVersion(21)
    """TODO: RENAME"""
    SHORT_GRASS = PackVersion(26)
    """Rename 'grass' to 'short_grass'"""
    COMPONENT = PackVersion(33)
    """Switch from NBT system to Component system"""
    LEGACY_FOLDER_RENAME = PackVersion(48)
    """Change 'functions' to 'function' etc."""
    PLS_RENAME_59 = PackVersion(59)
    """TODO: RENAME"""
    TEXT_COMPONENT = PackVersion(62)
    """Make text component to no longer require stringifying the JSON"""

    def __new__(cls, *args, **kwargs) -> "PackVersionFeature":
        raise TypeError("Don't instantiate this")
