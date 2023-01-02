from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..compile.tokenizer import Token


@dataclass(slots=True, frozen=False, eq=True)
class Item:
    item_type: str
    nbt: str

    def __str__(self) -> str:
        return self.item_type + (self.nbt if self.nbt != "" else "")


@dataclass(slots=True, frozen=False, eq=True)
class TemplateItem:
    char_id: str
    item: Item | None = None
    interactive_id: int | None = None

    def set_nbt(self) -> None:
        if self.item is None:
            raise ValueError
        self.item.nbt = f"{{{self.item.nbt[1:-1]}}},"


class GUIMode(Enum):
    ENTITY = "entity @s"
    BLOCK = "block ~ ~ ~"


class GUI:
    __slots__ = ("mode", "size", "template", "is_ready")
    mode: GUIMode
    size: tuple[int, int]
    """Row x Column"""
    template: list[TemplateItem]
    is_ready: bool
    DEFAULT_ITEM = Item(
        "gray_stained_glass_pane",
        nbt="""{display: {Name:'""'}}""")

    def __init__(self, mode: GUIMode, template: list[str]) -> None:
        self.is_ready = False
        self.mode = mode
        self.size = (len(template), len(template[0]))
        self.template = [TemplateItem(char)
                         for row in template for char in row]

    def set_item(self, slot: str, item: Item,
                 interactive_id: None = None) -> None:
        for template_item in self.template:
            if slot == template_item.char_id:
                if template_item.item is not None:
                    raise ValueError
                template_item.item = item
                template_item.interactive_id = interactive_id

    def set_to_default(self) -> None:
        self.is_ready = True
        for template_item in self.template:
            if template_item.item is not None:
                template_item.item = self.DEFAULT_ITEM

    def get_reset_commands(self) -> list[str]:
        return []


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
