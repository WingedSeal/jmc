from dataclasses import dataclass, field


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
    __slots__ = 'item', '__item_id_count'

    def __init__(self) -> None:
        self.item: dict[str, Item] = {}
        self.__item_id_count: int = 0

    def get_item_id(self) -> str:
        """
        Get item id for on_click feature of Item.create

        :return: Item ID
        """
        self.__item_id_count += 1
        return str(self.__item_id_count)
