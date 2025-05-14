from jmc.compile.pack_version import PackVersionFeature
from ..datapack_data import Item
from .utils import FormattedText, hash_string_to_string
from ..exception import JMCValueError
from ..tokenizer import Token, TokenType

from .jmc_function import JMCFunction


class ItemMixin(JMCFunction):
    def clone_item(
            self, item: "Item", modify_nbt: dict[str, Token] | None = None, modify_component: dict[str, Token] | None = None, error_token: Token | None = None) -> "Item":
        """
        Create new item from existing item

        :param item: An Item to copy from
        :param modify_nbt: NBT to modify, defaults to None
        :param modify_component: Component to modify, defaults to None
        :param error_token: Token to raise an error to, defaults to None
        :return: New Item
        """
        item_type = item.item_type
        nbt = dict(item.nbt)
        component = dict(item.component)
        if modify_nbt is None:
            modify_nbt = {}
        if modify_component is None:
            modify_component = {}
        for key, value_token in modify_nbt.items():
            if key in nbt:
                raise JMCValueError(
                    f"{key} is already inside the nbt",
                    value_token if error_token is None else error_token,
                    self.tokenizer)

            nbt[key] = value_token
        for key, value_token in modify_component.items():
            if key in component:
                raise JMCValueError(
                    f"{key} is already inside the component",
                    value_token if error_token is None else error_token,
                    self.tokenizer)

            component[key] = value_token
        is_component = self.datapack.version >= PackVersionFeature.COMPONENT
        return Item(
            item_type,
            self.datapack.token_dict_to_component(
                component, self.tokenizer, nbt) if is_component else self.datapack.token_dict_to_raw_js_object(nbt, self.tokenizer),
            nbt,
            component
        )

    def create_item(self, item_type_param: str = "itemType", display_name_param: str = "displayName",
                    lore_param: str = "lore", nbt_param: str = "nbt", component_param: str = "component", modify_nbt: dict[str, Token] | None = None, modify_component: dict[str, Token] | None = None) -> "Item":
        """
        Create new item from arguments given in the JMCFunction

        :param item_type_param: Paramter to access `self.args`,defaults to "displayName"
        :param display_name_param: Paramter to access `self.args`,defaults to "itemType"
        :param lore_param: Paramter to access `self.args`,defaults to "lore"
        :param nbt_param: Paramter to access `self.args`,defaults to "nbt"
        :param component_param: Paramter to access `self.args`,defaults to "component"
        :param modify_nbt: NBT to modify, defaults to None
        :param modify_component: Component to modify, defaults to None
        :return: Item
        """
        if modify_component is not None:
            assert self.datapack.version >= PackVersionFeature.COMPONENT
        if self.args[component_param]:
            self.datapack.version.require(
                PackVersionFeature.COMPONENT, self.raw_args[component_param].token, self.tokenizer, "Component is only available on at least pack format 33, use nbt instead")
        if self.args[nbt_param]:
            self.datapack.version.require(
                PackVersionFeature.COMPONENT, self.raw_args[nbt_param].token, self.tokenizer, "NBT is only available on pack format lower than 33, use component instead", is_lower=True)
        if modify_nbt is None:
            modify_nbt = {}
        if modify_component is None:
            modify_component = {}

        item_type = self.args[item_type_param]
        if item_type.startswith("minecraft:"):
            item_type = item_type[10:]
        if self.args[lore_param]:
            lores, _ = self.datapack.parse_list(
                self.raw_args[lore_param].token, self.tokenizer, TokenType.STRING)
        else:
            lores = []
        component: dict[str, Token] = {}
        nbt: dict[str, Token] = {}
        if self.args[nbt_param]:
            component = {}
            nbt = self.tokenizer.parse_js_obj(
                self.raw_args[nbt_param].token)
        elif self.args[component_param]:
            component = self.tokenizer.parse_component(
                self.raw_args[component_param].token)
            if "nbt" in component:
                nbt = self.tokenizer.parse_js_obj(
                    component["nbt"])
                del component["nbt"]
            else:
                nbt = {}

        is_component = self.datapack.version >= PackVersionFeature.COMPONENT
        for key, value_token in modify_nbt.items():
            if key in nbt:
                raise JMCValueError(
                    f"{key} is already inside the nbt",
                    value_token,
                    self.tokenizer)

            nbt[key] = value_token
        for key, value_token in modify_component.items():
            if key in component:
                raise JMCValueError(
                    f"{key} is already inside the component",
                    value_token,
                    self.tokenizer)

            component[key] = value_token

        if is_component:
            repr_ = (
                lambda x: x) if self.datapack.version >= PackVersionFeature.TEXT_COMPONENT else repr
            if self.args[display_name_param]:
                if "custom_name" in component:
                    raise JMCValueError(
                        "custom_name is already inside the component",
                        self.token,
                        self.tokenizer)
                name_ = self.format_text(
                    display_name_param,
                    is_default_no_italic=True,
                    is_allow_score_selector=False)
                component["custom_name"] = Token.empty(repr_(name_))
            if self.args[lore_param]:
                if "lore" in component:
                    raise JMCValueError(
                        "lore is already inside the component",
                        self.token,
                        self.tokenizer)
                lore_ = ",".join([repr_(str(FormattedText(lore, self.raw_args[lore_param].token, self.tokenizer, self.datapack, is_default_no_italic=True, is_allow_score_selector=False)))
                                  for lore in lores])
                component["lore"] = Token.empty(f"[{lore_}]")

        else:
            new_token_string = "{"
            if self.args[display_name_param]:
                if "display" in nbt:
                    raise JMCValueError(
                        "display is already inside the nbt",
                        self.token,
                        self.tokenizer)
                name_ = self.format_text(
                    display_name_param,
                    is_default_no_italic=True,
                    is_allow_score_selector=False)
                new_token_string += f"""Name:{repr(name_)}"""
            if self.args[lore_param]:
                lore_ = ",".join([repr(str(FormattedText(lore, self.raw_args[lore_param].token, self.tokenizer, self.datapack, is_default_no_italic=True, is_allow_score_selector=False)))
                                  for lore in lores])
                if self.args[display_name_param]:
                    new_token_string += ","
                new_token_string += f"""Lore:[{lore_}]"""
            new_token_string += "}"
            if self.args[display_name_param] or self.args[lore_param]:
                nbt["display"] = Token.empty(new_token_string)

        return Item(
            item_type,
            self.datapack.token_dict_to_component(
                component, self.tokenizer, nbt) if is_component else self.datapack.token_dict_to_raw_js_object(nbt, self.tokenizer),
            nbt,
            component,
        )


class EventMixin(JMCFunction):
    def add_event(self, criteria: str, command: str) -> None:
        """
        Add command that'll run on criteria event

        :param criteria: Minecraft criteria
        :param command: Command to run
        """
        self.add_events(criteria, [command])

    def add_events(self, criteria: str, commands: list[str]) -> None:
        """
        Add multiple commands that'll run on criteria event

        :param criteria: Minecraft criteria
        :param commands: Commands to run
        """
        criteria = criteria.replace("minecraft.", "")
        count = criteria.lower().replace(":", "_")
        if self.is_never_used("on_event", parameters=[criteria]):
            objective = f"on_event_{hash_string_to_string(criteria, 7)}"
            self.datapack.add_objective(
                objective, criteria)
            func_call = self.datapack.add_raw_private_function(
                "on_event", [f"scoreboard players set @s {objective} 0", *commands], count=count)
            self.datapack.add_tick_command(
                f"execute as @a[scores={{{objective}=1..}}] at @s run {func_call}")

        else:
            func = self.datapack.private_functions["on_event"][count]
            func.extend(
                commands
            )
