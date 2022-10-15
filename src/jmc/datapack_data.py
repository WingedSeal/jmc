from dataclasses import dataclass, field

JSON_TEXT_TYPE = dict[str, str | bool]


@dataclass(slots=True, frozen=True, eq=True)
class Item:
    item_type: str
    name: str
    lores: list[str]
    nbt: str
    on_click: str | None


class Data:
    """
    Data shared across all JMC function in the datapack
    """
    __slots__ = 'item', '__item_id_count'

    def __init__(self) -> None:
        self.item: dict[str, Item] = {}
        self.__item_id_count: int = 0

    def get_item_id(self) -> int:
        """
        Get item id for on_click feature of Item.create

        :return: Item ID
        """
        self.__item_id_count += 1
        return self.__item_id_count
