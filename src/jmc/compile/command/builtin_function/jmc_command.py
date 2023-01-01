"""Module containing JMCFunction subclasses for custom JMC function"""

import math
from typing import Iterator
from ...exception import JMCSyntaxException, JMCValueError
from ..utils import ArgType, FormattedText, NumberType
from ..jmc_function import JMCFunction, FuncType, func_property


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
        "tick": ArgType.SCOREBOARD_PLAYER
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
        if self.raw_args["tick"].arg_type == ArgType.INTEGER:
            return f'scoreboard players set {self.args["selector"]} {self.args["objective"]} {self.args["tick"]}'
        return f'scoreboard players operation {self.args["selector"]} {self.args["objective"]} = {self.args["tick"]}'


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
                self.token,
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
                self.token,
                self.tokenizer,
                suggestion=f"Use Item.create to make this item BEFORE using {self.call_string}"
            )
        nbt = self.tokenizer.parse_js_obj(
            self.raw_args["nbt"].token) if self.args["nbt"] else {}
        if "Item" in nbt:
            raise JMCValueError(
                f'`Item` key found inside Item.summon nbt argument.',
                self.token,
                self.tokenizer,
                suggestion=f"Remove `Item` in the nbt"
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
                self.token,
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
                self.token,
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
        points = []
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
        points = []
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
    call_string="Team.add",
    arg_type={
        "team": ArgType.KEYWORD,
        "displayName": ArgType.STRING
    },
    name="team_add",
    defaults={
        "displayName": ""
    }
)
class TeamAdd(JMCFunction):
    def call(self) -> str:
        command = f'team add {self.args["team"]}'
        if self.args["team"] in self.datapack.data.teams:
            team = self.datapack.data.teams[self.args["team"]]
            raise JMCValueError(
                f"Team {self.args['team']} was already defined",
                self.raw_args["team"].token,
                self.tokenizer, suggestion=f"It was defined at line {team[1].line} col {team[1].col}")
        self.datapack.data.teams[self.args["team"]] = (
            self.args["displayName"], self.raw_args["team"].token)
        if self.args["displayName"]:
            command += ' ' + self.format_text("displayName")
        return command


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
