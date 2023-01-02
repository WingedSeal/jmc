from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..compile.tokenizer import Token


@dataclass(slots=True, frozen=True, eq=True)
class Item:
    item_type: str
    nbt: str

    def __str__(self) -> str:
        return self.item_type + (self.nbt if self.nbt != "" else "")


@dataclass(slots=True, frozen=False, eq=True)
class TemplateItem:
    char_id: str
    items: list[Item] | None = None
    variable: tuple[str, str] | None = None
    interactive_id: int | None = None


class GUIMode(Enum):
    ENTITY = "entity @s"
    BLOCK = "block ~ ~ ~"


class GUI:
    __slots__ = ("mode", "size", "template", "item_types", "template_map")
    mode: GUIMode
    size: tuple[int, int]
    """Row x Column"""
    template: list[TemplateItem]
    item_types: set[str]
    template_map: dict[str, list[TemplateItem]]
    DEFAULT_ITEM = Item(
        "gray_stained_glass_pane",
        nbt="""{display: {Name:'""'}}""")

    def __init__(self, mode: GUIMode, template: list[str]) -> None:
        self.template_map = defaultdict(list)
        self.mode = mode
        self.size = (len(template), len(template[0]))
        self.template = [TemplateItem(char, [self.DEFAULT_ITEM])
                         for row in template for char in row]
        index = 0
        for row in template:
            for char in row:
                template_item = TemplateItem(char, [self.DEFAULT_ITEM])
                self.template.append(template_item)
                self.template_map[char].append(template_item)
                index += 1

    def set_item(self, slot: str, items: list[Item],
                 interactive_id: None = None) -> None:
        for item in items:
            self.item_types.add(item.item_type)
        for template_item in self.template_map[slot]:
            if template_item.items is not None:
                raise ValueError
            template_item.items = items
            template_item.interactive_id = interactive_id

    def get_reset_commands(self) -> list[str]:
        commands: list[str] = []
        for index, template_item in enumerate(self.template):
            if template_item.items is None:
                continue
            if len(template_item.items) == 1:
                commands.append(
                    f"item replace block ~ ~ ~ container.{index} with {template_item.items[0]} 1")
                continue
            if template_item.variable is None:
                raise ValueError("template_item.variable is None")

            commands.extend(
                f"execute if score {template_item.variable[1]} {template_item.variable[0]} matches {matched_index} run item replace block ~ ~ ~ container.{index} with {matched_item} 1" for matched_index, matched_item in enumerate(template_item.items))
        return commands


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
