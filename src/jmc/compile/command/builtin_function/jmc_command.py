"""Module containing JMCFunction subclasses for custom JMC function"""

import math
from typing import Iterator

from ....compile.utils import convention_jmc_to_mc
from ...exception import JMCSyntaxException, JMCValueError
from ..utils import ArgType, NumberType, find_scoreboard_player_type
from ..jmc_function import JMCFunction, FuncType, func_property
from .utils.isolated import IsolatedEnvironment


def drange(start: float | int, stop: float | int,
           step: float | int) -> Iterator[float | int]:
    """
    Similar to built-in range() function but with float

    :param start: Included starting point
    :param stop: Excluded ending point
    :param step: Step
    :yield: Float/Integer
    """
    result = start
    while result < stop:
        yield result
        result += step


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Timer.set",
    arg_type={
        "objective": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR,
        "tick": ArgType.SCOREBOARD_INT
    },
    name="timer_set"
)
class TimerSet(JMCFunction):
    """
    ```py
    TimerSet(objective, target_selector: selector, tick: number|$variable)
    ```
    Set entity's score to start the timer.
    """

    def call(self) -> str:
        tick_arg = find_scoreboard_player_type(
            self.raw_args["tick"].token, self.tokenizer)
        if isinstance(tick_arg.value, int):
            return f'scoreboard players set {self.args["selector"]} {self.args["objective"]} {self.args["tick"]}'
        return f'scoreboard players operation {self.args["selector"]} {self.args["objective"]} = {tick_arg.value[1]} {tick_arg.value[0]}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Item.clear",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR,
        "amount": ArgType.INTEGER
    },
    name="item_clear",
    defaults={
        "selector": "@s",
        "amount": "-1"
    }
)
class ItemClear(JMCFunction):
    def call(self) -> str:
        numerical_amount = float(self.args["amount"])
        if numerical_amount == -1:
            self.args["amount"] = ""
        elif numerical_amount < 0:
            raise JMCValueError(
                f'\'amount\' parameter must be greater than or equal to 0', self.raw_args[
                    "amount"].token, self.tokenizer,
            )

        if self.args["itemId"] not in self.datapack.data.item:
            raise JMCValueError(
                f'Item id: \'{self.args["itemId"]}\' is not defined.',
                self.raw_args["itemId"].token,
                self.tokenizer,
                suggestion=f"Use Item.create to make this item BEFORE using {self.call_string}"
            )
        return f'clear {self.args["selector"]} {self.datapack.data.item[self.args["itemId"]]} {self.args["amount"]}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Item.give",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR,
        "amount": ArgType.INTEGER
    },
    name="item_give",
    defaults={
        "selector": "@s",
        "amount": "1"
    },
    number_type={
        "amount": NumberType.ZERO_POSITIVE
    }
)
class ItemGive(JMCFunction):
    def call(self) -> str:
        if self.args["itemId"] not in self.datapack.data.item:
            raise JMCValueError(
                f'Item id: \'{self.args["itemId"]}\' is not defined.',
                self.raw_args["itemId"].token,
                self.tokenizer,
                suggestion=f"Use Item.create to make this item BEFORE using {self.call_string}"
            )
        return f'give {self.args["selector"]} {self.datapack.data.item[self.args["itemId"]]} {self.args["amount"]}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Item.summon",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "pos": ArgType.STRING,
        "count": ArgType.INTEGER,
        "nbt": ArgType.JS_OBJECT
    },
    name="item_summon",
    defaults={
        "pos": "~ ~ ~",
        "count": "1",
        "nbt": ""
    },
    number_type={
        "count": NumberType.POSITIVE
    }
)
class ItemSummon(JMCFunction):
    def call(self) -> str:
        if self.args["itemId"] not in self.datapack.data.item:
            raise JMCValueError(
                f'Item id: \'{self.args["itemId"]}\' is not defined.',
                self.raw_args["itemId"].token,
                self.tokenizer,
                suggestion=f"Use Item.create to make this item BEFORE using {self.call_string}"
            )
        nbt = self.tokenizer.parse_js_obj(
            self.raw_args["nbt"].token) if self.args["nbt"] else {}
        if "Item" in nbt:
            raise JMCValueError(
                '`Item` key found inside Item.summon nbt argument.',
                self.token,
                self.tokenizer,
                suggestion="Remove `Item` in the nbt"
            )
        return f'summon item {self.args["pos"]} {{Item:{{id:"{self.datapack.data.item[self.args["itemId"]].item_type}",Count:{self.args["count"]},tag:{self.datapack.data.item[self.args["itemId"]].nbt}}}{","+self.datapack.token_dict_to_raw_js_object(nbt, self.tokenizer)[1:-1] if nbt else ""}}}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Item.replaceBlock",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "pos": ArgType.STRING,
        "slot": ArgType.STRING,
        "count": ArgType.INTEGER
    },
    name="item_replace_block",
    defaults={
        "count": "1"
    },
    number_type={
        "count": NumberType.POSITIVE
    }
)
class ItemReplaceBlock(JMCFunction):
    def call(self) -> str:
        if self.args["itemId"] not in self.datapack.data.item:
            raise JMCValueError(
                f'Item id: \'{self.args["itemId"]}\' is not defined.',
                self.raw_args["itemId"].token,
                self.tokenizer,
                suggestion=f"Use Item.create to make this item BEFORE using {self.call_string}"
            )
        return f'item replace block {self.args["pos"]} {self.args["slot"]} with {self.datapack.data.item[self.args["itemId"]]} {self.args["count"]}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Item.replaceEntity",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR,
        "slot": ArgType.STRING,
        "count": ArgType.INTEGER
    },
    name="item_replace_entity",
    defaults={
        "count": "1"
    },
    number_type={
        "count": NumberType.POSITIVE
    }
)
class ItemReplaceEntity(JMCFunction):
    def call(self) -> str:
        if self.args["itemId"] not in self.datapack.data.item:
            raise JMCValueError(
                f'Item id: \'{self.args["itemId"]}\' is not defined.',
                self.raw_args["itemId"].token,
                self.tokenizer,
                suggestion=f"Use Item.create to make this item BEFORE using {self.call_string}"
            )
        return f'item replace entity {self.args["selector"]} {self.args["slot"]} with {self.datapack.data.item[self.args["itemId"]]} {self.args["count"]}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="JMC.put",
    arg_type={
        "command": ArgType.STRING,
    },
    name="jmc_put",
)
class JMCPut(JMCFunction):
    def call(self) -> str:
        return self.args["command"]


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Text.tellraw",
    arg_type={
        "selector": ArgType.SELECTOR,
        "message": ArgType.STRING,
    },
    name="text_tellraw",
)
class TextTellraw(JMCFunction):
    def call(self) -> str:
        return f'tellraw {self.args["selector"]} {self.format_text("message")}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="printf",
    arg_type={
        "text": ArgType.STRING,
    },
    name="printf",
)
class Printf(JMCFunction):
    def call(self) -> str:
        return f'tellraw @a {self.format_text("text")}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="print",
    arg_type={
        "value": ArgType.SCOREBOARD,
    },
    name="print",
)
class Print(JMCFunction):
    def call(self) -> str:
        scoreboard_player = find_scoreboard_player_type(
            self.raw_args["value"].token, self.tokenizer)
        if isinstance(scoreboard_player.value, int):
            raise ValueError("value is int")
        name = scoreboard_player.value[1]
        obj = scoreboard_player.value[0]
        return 'tellraw @a {"score":{"name":"%s","objective":"%s"}}' % (
            name, obj)


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Text.title",
    arg_type={
        "selector": ArgType.SELECTOR,
        "message": ArgType.STRING,
    },
    name="text_title",
)
class TextTitle(JMCFunction):
    def call(self) -> str:
        return f'title {self.args["selector"]} title {self.format_text("message")}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Text.subtitle",
    arg_type={
        "selector": ArgType.SELECTOR,
        "message": ArgType.STRING,
    },
    name="text_subtitle",
)
class TextSubtitle(JMCFunction):
    def call(self) -> str:
        return f'title {self.args["selector"]} subtitle {self.format_text("message")}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Text.actionbar",
    arg_type={
        "selector": ArgType.SELECTOR,
        "message": ArgType.STRING,
    },
    name="text_actionbar",
)
class TextActionbar(JMCFunction):
    def call(self) -> str:
        return f'title {self.args["selector"]} actionbar {self.format_text("message")}'


def __normalize_decimal(n: float):
    """
    Parse float into string

    :param n: _description_
    """
    if n == 0:
        return ""
    stripped = f"{n:.10f}"  # .rstrip('0').rstrip('.')
    return stripped


def points_to_commands(points: list[tuple[float, float, float]], particle: str,
                       speed: str, count: str, mode: str, notation: str = "^") -> list[str]:
    """
    Parse list of points(x,y,z position) into particle commands

    :param points: List of points(x,y,z position)
    :param particle: particle type
    :param speed: particle speed
    :param count: particle count
    :param mode: particle mode
    :param notation: Notation (~) or (^)
    :return: particle commands
    """
    commands = []
    for x_pos, y_pos, z_pos in points:
        commands.append(
            f"particle {particle} {notation}{__normalize_decimal(x_pos)} {notation}{__normalize_decimal(y_pos)} {notation}{__normalize_decimal(z_pos)} 0 0 0 {speed} {count} {mode}")
    return commands


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.circle",
    arg_type={
        "particle": ArgType.STRING,
        "radius": ArgType.FLOAT,
        "spread": ArgType.INTEGER,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_circle",
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    },
    number_type={
        "spread": NumberType.POSITIVE,
        "radius": NumberType.POSITIVE,
        "count": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleCircle(JMCFunction):
    def draw(self, radius: float,
             spread: int) -> list[tuple[float, float, float]]:
        """
        Draw particles

        :param radius: Radius of the circle
        :param spread: How close are particles to each other
        :return: List of coordinate for each particles
        """
        points: list[tuple[float, float, float]] = []
        angle = 2 * math.pi / spread
        for i in drange(0, spread, angle):
            points.append((radius * math.cos(i), 0.0, radius * math.sin(i)))
        return points

    def call(self) -> str:
        if self.args["mode"] not in {"force", "normal"}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    float(self.args["radius"]),
                    int(self.args["spread"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.sphere",
    arg_type={
        "particle": ArgType.STRING,
        "radius": ArgType.FLOAT,
        "spread": ArgType.INTEGER,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_sphere",
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    },
    number_type={
        "spread": NumberType.POSITIVE,
        "radius": NumberType.POSITIVE,
        "count": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleSphere(JMCFunction):
    def draw(self, radius: float,
             spread: int) -> list[tuple[float, float, float]]:
        """
        Draw particles

        :param radius: Radius of the sphere
        :param spread: How close are particles to each other
        :return: List of coordinate for each particles
        """
        points: list[tuple[float, float, float]] = []
        angle = 2 * math.pi / spread
        for theta in drange(0, spread, angle):
            for phi in drange(0, spread, angle):
                points.append(
                    (radius *
                     math.sin(theta) *
                        math.cos(phi),
                        radius *
                        math.cos(theta),
                        radius *
                        math.sin(theta) *
                        math.sin(phi)))
        return points

    def call(self) -> str:
        if self.args["mode"] not in {"force", "normal"}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    float(self.args["radius"]),
                    int(self.args["spread"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.square",
    arg_type={
        "particle": ArgType.STRING,
        "length": ArgType.FLOAT,
        "spread": ArgType.INTEGER,
        "align": ArgType.KEYWORD,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_square",
    defaults={
        "speed": "1",
        "count": "1",
        "align": "corner",
        "mode": "normal"
    },
    number_type={
        "spread": NumberType.POSITIVE,
        "length": NumberType.POSITIVE,
        "count": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleSquare(JMCFunction):
    def draw(self, length: float, spread: int,
             align: str) -> list[tuple[float, float, float]]:
        """
        Draw particles

        :param length: Side length of the square
        :param spread: How close are particles to each other
        :param align: Whether to the current position should be the center or the corner
        :return: List of coordinate for each particles
        """
        points: list[tuple[float, float, float]] = []
        if spread == 1:
            return [(0.0, 0.0, 0.0)]
        spacing = length / (spread - 1)
        start: float = 0
        if align == "center":
            start -= length / 2
        stop = start + length

        for i in drange(start, stop, spacing):
            points.append((start, 0.0, i + spacing))  # west
            points.append((stop, 0.0, i))  # east
            points.append((i, 0.0, start))  # north
            points.append((i + spacing, 0.0, stop))  # south

        return points

    def call(self) -> str:
        if self.args["align"] not in {"corner", "center"}:
            raise JMCSyntaxException(
                f"Unrecognized alignment, '{self.args['align']}' Available alignments are 'corner' and 'center'", self.raw_args["mode"].token, self.tokenizer)

        if self.args["mode"] not in {"force", "normal"}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    float(self.args["length"]),
                    int(self.args["spread"]),
                    str(self.args["align"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.cube",
    arg_type={
        "particle": ArgType.STRING,
        "length": ArgType.FLOAT,
        "spread": ArgType.INTEGER,
        "align": ArgType.KEYWORD,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_cube",
    defaults={
        "speed": "1",
        "count": "1",
        "align": "corner",
        "mode": "normal"
    },
    number_type={
        "spread": NumberType.POSITIVE,
        "length": NumberType.POSITIVE,
        "count": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleCube(JMCFunction):
    def draw(self, length: float, spread: int,
             align: str) -> list[tuple[float, float, float]]:
        """
        Draw particles

        :param length: Side length of the cube
        :param spread: How close are particles to each other
        :param align: Whether to the current position should be the center or the corner
        :return: List of coordinate for each particles
        """
        points: list[tuple[float, float, float]] = []
        if spread == 1:
            return [(0.0, 0.0, 0.0)]
        spacing = length / (spread - 1)
        start: float = 0
        if align == "center":
            start -= length / 2
        stop = start + length

        for i in drange(start, stop, spacing):
            points.append((start, start, i + spacing))  # lower west edge
            points.append((stop, start, i))  # lower east edge
            points.append((i, start, start))  # lower north edge
            points.append((i + spacing, start, stop))  # lower south edge

            points.append((start, i, start))  # northwest edge
            points.append((stop, i, start))  # northeast edge
            points.append((start, i, stop))  # southwest edge
            points.append((stop, i + spacing, stop))  # southeast edge

            points.append((start, stop, i))  # upper west edge
            points.append((stop, stop, i))  # upper east edge
            points.append((i, stop, start))  # upper north edge
            points.append((i, stop, stop))  # upper south edge

        return points

    def call(self) -> str:
        if self.args["align"] not in {"corner", "center"}:
            raise JMCSyntaxException(
                f"Unrecognized alignment, '{self.args['align']}' Available alignments are 'corner' and 'center'", self.raw_args["mode"].token, self.tokenizer)

        if self.args["mode"] not in {"force", "normal"}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    float(self.args["length"]),
                    int(self.args["spread"]),
                    str(self.args["align"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.spiral",
    arg_type={
        "particle": ArgType.STRING,
        "radius": ArgType.FLOAT,
        "height": ArgType.FLOAT,
        "spread": ArgType.INTEGER,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_spiral",
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    },
    number_type={
        "spread": NumberType.POSITIVE,
        "radius": NumberType.POSITIVE,
        "height": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleSpiral(JMCFunction):
    def draw(self, radius: float, height: float,
             spread: int) -> list[tuple[float, float, float]]:
        """
        Draw particles

        :param radius: Radius of the spiral
        :param height: Height of the spiral
        :param spread: How close are particles to each other
        :return: List of coordinate for each particles
        """
        points: list[tuple[float, float, float]] = []
        angle = 2 * math.pi / spread
        d_y = height / spread
        for i in range(spread):
            points.append((
                radius * math.cos(i * angle),
                i * d_y,
                radius * math.sin(i * angle)))
        return points

    def call(self) -> str:
        if self.args["mode"] not in {"force", "normal"}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    float(self.args["radius"]),
                    float(self.args["height"]),
                    int(self.args["spread"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.helix",
    arg_type={
        "particle": ArgType.STRING,
        "radius": ArgType.FLOAT,
        "height": ArgType.FLOAT,
        "spread": ArgType.INTEGER,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_spiral",
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    },
    number_type={
        "spread": NumberType.POSITIVE,
        "radius": NumberType.POSITIVE,
        "height": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleHelix(ParticleSpiral):
    pass


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.cylinder",
    arg_type={
        "particle": ArgType.STRING,
        "radius": ArgType.FLOAT,
        "height": ArgType.FLOAT,
        "spreadXZ": ArgType.INTEGER,
        "spreadY": ArgType.INTEGER,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_cylinder",
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    },
    number_type={
        "spreadXZ": NumberType.POSITIVE,
        "spreadY": NumberType.POSITIVE,
        "radius": NumberType.POSITIVE,
        "height": NumberType.POSITIVE,
        "count": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleCylinder(JMCFunction):
    def draw(self, radius: float, height: float, spread_xz: int,
             spread_y: int) -> list[tuple[float, float, float]]:
        """
        Draw particles

        :param radius: Radius of the cylinder
        :param height: Height of the cylinder
        :param spread: How close are particles to each other in xz plane
        :param spread: How close are particles to each other in y axis
        :return: List of coordinate for each particles
        """
        points = []
        d_y = height / spread_y
        for y in range(spread_y):
            angle = 2 * math.pi / spread_xz
            for i in drange(0, spread_xz, angle):
                points.append(
                    (radius * math.cos(i), y * d_y, radius * math.sin(i)))
        return points

    def call(self) -> str:
        if self.args["mode"] not in {"force", "normal"}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    float(self.args["radius"]),
                    float(self.args["height"]),
                    int(self.args["spreadXZ"]),
                    int(self.args["spreadY"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Particle.line",
    arg_type={
        "particle": ArgType.STRING,
        "distance": ArgType.FLOAT,
        "spread": ArgType.INTEGER,
        "speed": ArgType.INTEGER,
        "count": ArgType.INTEGER,
        "mode": ArgType.KEYWORD,
    },
    name="particle_line",
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    },
    number_type={
        "spread": NumberType.POSITIVE,
        "distance": NumberType.POSITIVE,
        "count": NumberType.POSITIVE,
        "speed": NumberType.ZERO_POSITIVE
    }
)
class ParticleLine(JMCFunction):
    def draw(self, distance: float,
             spread: int) -> list[tuple[float, float, float]]:
        """
        Draw particles

        :param distance: How long the line is
        :param spread: How close are particles to each other
        :return: List of coordinate for each particles
        """
        return [(0, 0, n) for n in drange(1, distance + 1, distance / spread)]

    def call(self) -> str:
        if self.args["mode"] not in {"force", "normal"}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    float(self.args["distance"]),
                    int(self.args["spread"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Scoreboard.add",
    arg_type={
        "objective": ArgType.KEYWORD,
        "criteria": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
    },
    name="scoreboard_add",
    defaults={
        "criteria": "dummy",
        "displayName": ""
    }
)
class ScoreboardAdd(JMCFunction):
    def call(self) -> str:
        command = f'scoreboard objectives add {self.args["objective"]} {self.args["criteria"]}'
        if self.args["objective"] in self.datapack.data.scoreboards:
            scoreboard = self.datapack.data.scoreboards[self.args["objective"]]
            raise JMCValueError(
                f"Objective {self.args['objective']} was already defined as {scoreboard[1]}",
                self.raw_args["objective"].token,
                self.tokenizer, suggestion=f"It was defined at line {scoreboard[2].line} col {scoreboard[2].col}")
        self.datapack.data.scoreboards[self.args["objective"]] = (
            self.args["criteria"], self.args["displayName"], self.raw_args["objective"].token)
        if self.args["displayName"]:
            command += ' ' + self.format_text("displayName")
        return command


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Team.prefix",
    arg_type={
        "team": ArgType.KEYWORD,
        "prefix": ArgType.STRING,
    },
    name="team_prefix"
)
class TeamPrefix(JMCFunction):
    def call(self) -> str:
        return f"team modify {self.args['team']} prefix {self.format_text('prefix', is_allow_score_selector=False)}"


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Team.suffix",
    arg_type={
        "team": ArgType.KEYWORD,
        "suffix": ArgType.STRING,
    },
    name="team_suffix"
)
class TeamSuffix(JMCFunction):
    def call(self) -> str:
        return f"team modify {self.args['team']} suffix {self.format_text('suffix', is_allow_score_selector=False)}"


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Bossbar.add",
    arg_type={
        "id": ArgType.KEYWORD,
        "name": ArgType.STRING
    },
    name="bossbar_add"
)
class BossbarAdd(JMCFunction):
    def call(self) -> str:
        if self.args["id"] in self.datapack.data.bossbars:
            bossbar = self.datapack.data.bossbars[self.args["id"]]
            raise JMCValueError(
                f"Bossbar {self.args['id']} was already defined",
                self.raw_args["id"].token,
                self.tokenizer, suggestion=f"It was defined at line {bossbar[1].line} col {bossbar[1].col}")
        self.datapack.data.bossbars[self.args["id"]] = (
            self.args["name"], self.raw_args["id"].token)
        return f'bossbar add {self.args["id"]} {self.format_text("name")}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Bossbar.setName",
    arg_type={
        "id": ArgType.KEYWORD,
        "name": ArgType.STRING
    },
    name="bossbar_set_name"
)
class BossbarSetName(JMCFunction):
    def call(self) -> str:
        return f'bossbar set {self.args["id"]} name {self.format_text("name")}'


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="GUI.run",
    arg_type={
        "name": ArgType.KEYWORD,
    },
    name="gui_run"
)
class GUIRun(JMCFunction):

    def call(self) -> str:
        name = convention_jmc_to_mc(
            self.raw_args["name"].token, self.tokenizer, self.prefix)
        if name not in self.datapack.data.guis:
            raise JMCValueError(
                f"GUI Template '{name}' was never defined",
                self.raw_args["name"].token,
                self.tokenizer)
        gui = self.datapack.data.guis[name]
        if not gui.is_created:
            raise JMCValueError(
                f"GUI Template '{name}' was never created",
                self.raw_args["name"].token,
                self.tokenizer, suggestion="Use GUI.create BEFORE running")

        if self.is_never_used():
            self.datapack.add_tick_command(
                "kill @e[type=minecraft:item,nbt={Item:{tag:{__gui__:{}}}}]", is_after=True)

        return self.datapack.call_func(f"gui/{name}", "run")


MINECRAFT_ADVANCEMENTS = {
    "adventure/root",
    "adventure/voluntary_exile",
    "adventure/kill_a_mob",
    "adventure/trade",
    "adventure/honey_block_slide",
    "adventure/ol_betsy",
    "adventure/sleep_in_bed",
    "adventure/hero_of_the_village",
    "adventure/throw_trident",
    "adventure/shoot_arrow",
    "adventure/kill_all_mobs",
    "adventure/totem_of_undying",
    "adventure/summon_iron_golem",
    "adventure/two_birds_one_arrow",
    "adventure/whos_the_pillager_now",
    "adventure/arbalistic",
    "adventure/adventuring_time",
    "adventure/very_very_frightening",
    "adventure/sniper_duel",
    "adventure/bullseye",
    "end/root",
    "end/kill_dragon",
    "end/dragon_egg",
    "end/enter_end_gateway",
    "end/respawn_dragon",
    "end/dragon_breath",
    "end/find_end_city",
    "end/elytra",
    "end/levitate",
    "husbandry/root",
    "husbandry/safely_harvest_honey",
    "husbandry/breed_an_animal",
    "husbandry/tame_an_animal",
    "husbandry/fishy_business",
    "husbandry/silk_touch_nest",
    "husbandry/plant_seed",
    "husbandry/breed_all_animals",
    "husbandry/complete_catalogue",
    "husbandry/tactical_fishing",
    "husbandry/balanced_diet",
    "husbandry/break_diamond_hoe",
    "husbandry/obtain_netherite_hoe",
    "nether/root",
    "nether/fast_travel",
    "nether/find_fortress",
    "nether/return_to_sender",
    "nether/obtain_blaze_rod",
    "nether/get_wither_skull",
    "nether/uneasy_alliance",
    "nether/brew_potion",
    "nether/summon_wither",
    "nether/all_potions",
    "nether/create_beacon",
    "nether/all_effects",
    "nether/create_full_beacon",
    "nether/find_bastion",
    "nether/obtain_ancient_debris",
    "nether/obtain_crying_obsidian",
    "nether/distract_piglin",
    "nether/ride_strider",
    "nether/loot_bastion",
    "nether/use_lodestone",
    "nether/netherite_armor",
    "nether/charge_respawn_anchor",
    "nether/explore_nether",
    "story/root",
    "story/mine_stone",
    "story/upgrade_tools",
    "story/smelt_iron",
    "story/obtain_armor",
    "story/lava_bucket",
    "story/iron_tools",
    "story/deflect_arrow",
    "story/form_obsidian",
    "story/mine_diamond",
    "story/enter_the_nether",
    "story/shiny_gear",
    "story/enchant_item",
    "story/cure_zombie_villager",
    "story/follow_ender_eye",
    "story/enter_the_end"
}


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Advancement.revoke",
    name="advancement_revoke",
    arg_type={
        "target": ArgType.SELECTOR,
        "type": ArgType.KEYWORD,
        "advancement": ArgType.KEYWORD,
        "namespace": ArgType.KEYWORD
    },
    defaults={
        "advancement": "",
        "namespace": ""
    }
)
class AdvancementRevoke(JMCFunction):
    def call(self) -> str:
        advancement = self.args["advancement"]
        target = self.args["target"]
        type_ = self.args["type"]
        namespace = self.datapack.namespace if self.args["namespace"] == "" else self.args["namespace"]

        if namespace == "minecraft":
            if not (
                    f"minecraft/advancements/{advancement}" in MINECRAFT_ADVANCEMENTS or f"minecraft/advancements/{advancement}" in self.datapack.jsons):
                raise JMCValueError(
                    f"'{advancement}' advancement in '{namespace}' is not defined or missing",
                    self.raw_args["advancement"].token,
                    self.tokenizer
                )
        elif advancement:
            if f"advancements/{advancement}" not in self.datapack.jsons:
                raise JMCValueError(
                    f"'{advancement}' advancement in '{namespace}' is not defined or missing",
                    self.raw_args["advancement"].token,
                    self.tokenizer
                )

        if type_ not in {"everything", "from", "only", "through", "until"}:
            raise JMCValueError(
                f"'{type_}' is not an valid argument",
                self.raw_args["type"].token,
                self.tokenizer,
                suggestion="valid arguments are: everything,from,only,through,until"
            )

        if type_ == "everything" and advancement:
            raise JMCValueError(
                "Extra argument: 'advancement'",
                self.raw_args["advancement"].token,
                self.tokenizer
            )

        elif type_ != "everything" and not advancement:
            raise JMCValueError(
                "Missing argument 'advancement'",
                self.raw_args["advancement"].token,
                self.tokenizer
            )

        resource_location = f" {namespace}:{advancement}" if (
            type_ != "everything") else ""
        return f"advancement revoke {target} {type_}{resource_location}"


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Advancement.grant",
    name="advancement_grant",
    arg_type={
        "target": ArgType.SELECTOR,
        "type": ArgType.KEYWORD,
        "advancement": ArgType.KEYWORD,
        "namespace": ArgType.KEYWORD
    },
    defaults={
        "advancement": "",
        "namespace": ""
    }
)
class AdvancementGrant(JMCFunction):
    def call(self) -> str:
        advancement = self.args["advancement"]
        target = self.args["target"]
        type_ = self.args["type"]
        namespace = self.datapack.namespace if self.args["namespace"] == "" else self.args["namespace"]

        if namespace == "minecraft":
            if not (
                    f"minecraft/advancements/{advancement}" in MINECRAFT_ADVANCEMENTS or f"minecraft/advancements/{advancement}" in self.datapack.jsons):
                raise JMCValueError(
                    f"'{advancement}' advancement in '{namespace}' is not defined or missing",
                    self.raw_args["advancement"].token,
                    self.tokenizer
                )
        elif advancement:
            if f"advancements/{advancement}" not in self.datapack.jsons:
                raise JMCValueError(
                    f"'{advancement}' advancement in '{namespace}' is not defined or missing",
                    self.raw_args["advancement"].token,
                    self.tokenizer
                )

        if type_ not in {"everything", "from", "only", "through", "until"}:
            raise JMCValueError(
                f"'{type_}' is not an valid argument",
                self.raw_args["type"].token,
                self.tokenizer,
                suggestion="valid arguments are: everything,from,only,through,until"
            )

        if type_ == "everything" and advancement:
            raise JMCValueError(
                "Extra argument: 'advancement'",
                self.raw_args["advancement"].token,
                self.tokenizer
            )

        elif type_ != "everything" and not advancement:
            raise JMCValueError(
                "Missing argument: 'advancement'",
                self.raw_args["advancement"].token,
                self.tokenizer
            )

        resource_location = f" {namespace}:{advancement}" if (
            type_ != "everything") else ""
        return f"advancement grant {target} {type_}{resource_location}"


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Entity.launch",
    arg_type={
        "power": ArgType.FLOAT
    },
    name="entity_launch",
    defaults={
        "power": "1"
    },
    number_type={
        "power": NumberType.NON_ZERO
    }
)
class EntityLaunch(JMCFunction):
    def call(self) -> str:
        if self.is_never_used(self.name, [self.args["power"]]):
            self.datapack.add_raw_private_function(
                self.name,
                [f"execute positioned 0.0 0.0 0.0 run tp ^ ^ ^{self.args['power']}",
                 f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} Motion set from entity @s Pos",
                 "tp ~ ~ ~",
                 f"data modify entity @s Motion set from storage {self.datapack.namespace}:{self.datapack.storage_name} Motion"],
                self.args["power"]
            )
        return self.datapack.call_func(self.name, self.args["power"])


ISOLATED_ENVIRONMENT = IsolatedEnvironment("emit")


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="JMC.python",
    name="jmc_python",
    arg_type={
        "pythonCode": ArgType.STRING,
        "env": ArgType.STRING
    },
    defaults={
        "env": ""
    }
)
class JMCPython(JMCFunction):
    def clear_indent(self, string: str, indent: str) -> str:
        if not string:
            return string
        if string.startswith(indent):
            return string[len(indent):]
        raise JMCSyntaxException(
            "Invalid indentation when trimming indentation",
            self.raw_args["pythonCode"].token,
            self.tokenizer, suggestion=string, col_length=False, display_col_length=False)

    def call(self) -> str:
        if not self.args["pythonCode"]:
            return ""

        python_lines = self.args["pythonCode"].split("\n")
        indent = python_lines[0][:len(
            python_lines[0]) - len(python_lines[0].lstrip())]
        if not indent:
            python_code = self.args["pythonCode"]
        else:
            python_code = "\n".join(self.clear_indent(line, indent)
                                    for line in python_lines)
        try:
            return ISOLATED_ENVIRONMENT.run(
                python_code, self.args["env"] if self.args["env"] else None)
        except Exception as error:
            raise JMCValueError(
                "An exception occured in JMC.python",
                self.raw_args["pythonCode"].token,
                self.tokenizer, suggestion=str(error), col_length=False, display_col_length=False)


@func_property(
    func_type=FuncType.JMC_COMMAND,
    call_string="Array.forEach",
    name="array_for_each",
    arg_type={
        "target": ArgType.STRING,
        "path": ArgType.STRING,
        "function": ArgType.ARROW_FUNC
    }
)
class ArrayForEach(JMCFunction):
    def call(self) -> str:
        length = "__length__"
        current = "__current__"
        count = self.datapack.get_count("array")
        loop_func = self.datapack.add_raw_private_function("array", [
            self.args["function"],
            f"data modify storage {self.args['target']} {self.args['path']} append from storage {self.args['target']} {self.args['path']}[0]",
            f"data remove storage {self.args['target']} {self.args['path']}[0]",
            f"scoreboard players add {current} {self.datapack.var_name} 1",
            f"execute if score {current} {self.datapack.var_name} < {length} {self.datapack.var_name} run {self.datapack.call_func('array', count)}"
        ], count)
        return f"""execute store result score {length} {self.datapack.var_name} run data get storage {self.args["target"]} {self.args["path"]}
scoreboard players set {current} {self.datapack.var_name} 0
execute if score {current} {self.datapack.var_name} < {length} {self.datapack.var_name} run {loop_func}"""
