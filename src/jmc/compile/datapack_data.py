from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..compile.tokenizer import Token


@dataclass(slots=True, frozen=True, eq=True)
class Item:
    item_type: str
    nbt: str

    def __str__(self) -> str:
        return self.item_type + (self.nbt if self.nbt != "" else "")


class Data:
    """
    Data shared across all JMC function in the datapack
    """
    __slots__ = (
        "item",
        "__item_id_count",
        "condition_count",
        "__bool_result_count",
        "scoreboards",
        "teams",
        "bossbars")

    def __init__(self) -> None:
        self.item: dict[str, Item] = {}
        self.__item_id_count = 0
        self.condition_count = 0  # Used in condition.py
        self.__bool_result_count = -1  # Used in BOOL_FUNCTION
        self.scoreboards: dict[str, tuple[str, str, "Token"]] = {}
        self.teams: dict[str, tuple[str, "Token"]] = {}
        self.bossbars: dict[str, tuple[str, "Token"]] = {}

    def get_item_id(self) -> str:
        """
        Get item id for on_click feature of Item.create (starts at 1)

        :return: Item ID
        """
        self.__item_id_count += 1
        return str(self.__item_id_count)

    def get_current_bool_result(self) -> str:
        """
        Get bool result string (variable) for complex bool function (starts at 0)

        :return: __bool_result_n
        .. example::
        >>> data.get_current_bool_result()
        "__bool_result__0"
        >>> data.get_current_bool_result()
        "__bool_result__1"
        """
        self.__bool_result_count += 1
        return f"__bool_result__{self.__bool_result_count}"
