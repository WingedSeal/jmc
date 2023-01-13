from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..compile.tokenizer import Token

@dataclass
class MinecraftAdvancements:
    advancements: list[str] = field(default_factory=lambda: [
        'adventure/root',
        'adventure/voluntary_exile',
        'adventure/kill_a_mob',
        'adventure/trade',
        'adventure/honey_block_slide',
        'adventure/ol_betsy',
        'adventure/sleep_in_bed',
        'adventure/hero_of_the_village',
        'adventure/throw_trident',
        'adventure/shoot_arrow',
        'adventure/kill_all_mobs',
        'adventure/totem_of_undying',
        'adventure/summon_iron_golem',
        'adventure/two_birds_one_arrow',
        'adventure/whos_the_pillager_now',
        'adventure/arbalistic',
        'adventure/adventuring_time',
        'adventure/very_very_frightening',
        'adventure/sniper_duel',
        'adventure/bullseye',
        'end/root',
        'end/kill_dragon',
        'end/dragon_egg',
        'end/enter_end_gateway',
        'end/respawn_dragon',
        'end/dragon_breath',
        'end/find_end_city',
        'end/elytra',
        'end/levitate',
        'husbandry/root',
        'husbandry/safely_harvest_honey',
        'husbandry/breed_an_animal',
        'husbandry/tame_an_animal',
        'husbandry/fishy_business',
        'husbandry/silk_touch_nest',
        'husbandry/plant_seed',
        'husbandry/breed_all_animals',
        'husbandry/complete_catalogue',
        'husbandry/tactical_fishing',
        'husbandry/balanced_diet',
        'husbandry/break_diamond_hoe',
        'husbandry/obtain_netherite_hoe',
        'nether/root',
        'nether/fast_travel',
        'nether/find_fortress',
        'nether/return_to_sender',
        'nether/obtain_blaze_rod',
        'nether/get_wither_skull',
        'nether/uneasy_alliance',
        'nether/brew_potion',
        'nether/summon_wither',
        'nether/all_potions',
        'nether/create_beacon',
        'nether/all_effects',
        'nether/create_full_beacon',
        'nether/find_bastion',
        'nether/obtain_ancient_debris',
        'nether/obtain_crying_obsidian',
        'nether/distract_piglin',
        'nether/ride_strider',
        'nether/loot_bastion',
        'nether/use_lodestone',
        'nether/netherite_armor',
        'nether/charge_respawn_anchor',
        'nether/explore_nether',
        'story/root',
        'story/mine_stone',
        'story/upgrade_tools',
        'story/smelt_iron',
        'story/obtain_armor',
        'story/lava_bucket',
        'story/iron_tools',
        'story/deflect_arrow',
        'story/form_obsidian',
        'story/mine_diamond',
        'story/enter_the_nether',
        'story/shiny_gear',
        'story/enchant_item',
        'story/cure_zombie_villager',
        'story/follow_ender_eye',
        'story/enter_the_end'
    ])

@dataclass(slots=True, frozen=True, eq=True)
class Item:
    item_type: str
    nbt: str
    raw_nbt: dict[str, "Token"]

    def __str__(self) -> str:
        return self.item_type + (self.nbt if self.nbt != "" else "")


@dataclass(slots=True, frozen=False, eq=True)
class TemplateItem:
    char_id: str
    items: list[Item] | Item | None = None
    variable: str | None = None
    interactive_id: str | None = None
    on_click: str = ""
    container_changed: list[str] = field(default_factory=list)
    """Commands to run when the container changes"""


@dataclass(slots=True, frozen=True)
class GUIModeDetail:
    get: str
    container: str


class GUIMode(Enum):
    ENTITY = ("container", "entity @s", "Items")
    BLOCK = ("container", "block ~ ~ ~", "Items")
    ENDERCHEST = ("enderchest", "entity @s", "EnderItems")
    PLAYER = ("container", "entity @s", "Inventory")


class GUI:
    __slots__ = (
        "mode",
        "size",
        "name",
        "template",
        "item_types",
        "template_map",
        "is_created",
        "default_item")
    mode: GUIMode
    size: tuple[int, int]
    """Row x Column"""
    template: list[TemplateItem]
    interactions: list[str]
    """List of minecraft commands that'll be mapped to its index as interaction_id"""
    item_types: set[str]
    template_map: dict[str, list[TemplateItem]]
    is_created: bool
    default_item: Item

    def __init__(self, name: str, mode: GUIMode, template: list[str]) -> None:
        self.default_item = Item(
            "gray_stained_glass_pane",
            nbt="""{display:{Name:'""'},__gui__:{name:%s}}""" % repr(name),
            raw_nbt={})
        self.name = name
        self.is_created = False
        self.template_map = defaultdict(list)
        self.mode = mode
        self.size = (len(template), len(template[0]))
        self.template = []
        self.item_types = {"gray_stained_glass_pane"}
        index = 0
        for row in template:
            for char in row:
                template_item = TemplateItem(char, self.default_item)
                self.template.append(template_item)
                self.template_map[char].append(template_item)
                index += 1

    @property
    def length(self) -> int:
        empty = 0
        for template_item in self.template:
            if template_item.items is None:
                empty += 1
        return self.size[0] * self.size[1] - empty

    def get_reset_commands(self) -> list[str]:
        commands: list[str] = []
        for index, template_item in enumerate(self.template):
            if template_item.items is None:
                continue
            if isinstance(template_item.items, Item):
                commands.append(
                    f"item replace {self.mode.value[1]} {self.mode.value[0]}.{index} with {template_item.items} 1")
                continue
            if template_item.variable is None:
                raise ValueError("template_item.variable is None")

            commands.extend(
                f"execute if score {template_item.variable} matches {matched_index} run item replace {self.mode.value[1]} {self.mode.value[0]}.{index} with {matched_item} 1" for matched_index, matched_item in enumerate(template_item.items))
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
        "bossbars",
        "guis")

    def __init__(self) -> None:
        self.item: dict[str, Item] = {}
        self.__item_id_count = 0
        self.condition_count = 0  # Used in condition.py
        self.__bool_result_count = -1  # Used in BOOL_FUNCTION
        self.scoreboards: dict[str, tuple[str, str, "Token"]] = {}
        self.teams: dict[str, tuple[str, "Token"]] = {}
        self.bossbars: dict[str, tuple[str, "Token"]] = {}
        self.guis: dict[str, GUI] = {}

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
