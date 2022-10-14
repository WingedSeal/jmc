from dataclasses import dataclass, field

JSON_TEXT_TYPE = dict[str, str | bool]


@dataclass(slots=True, frozen=True, eq=True)
class Item:
    name: JSON_TEXT_TYPE
    lores: list[JSON_TEXT_TYPE]
    nbt: str


@dataclass(slots=True)
class Data:
    item: dict[str, Item] = field(default_factory=dict)
