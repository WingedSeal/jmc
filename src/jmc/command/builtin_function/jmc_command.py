"""Module containing JMCFunction subclasses for custom JMC function"""

import math
from typing import Iterator
from ...exception import JMCSyntaxException
from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property


def drange(start: float|int, stop: float|int, step: float|int) -> Iterator[float|int]:
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
    func_type=FuncType.jmc_command,
    call_string='Timer.set',
    arg_type={
        "objective": ArgType.keyword,
        "target_selector": ArgType.selector,
        "tick": ArgType.scoreboard_player
    },
    name='timer_set'
)
class TimerSet(JMCFunction):
    """
    ```py
    TimerSet(objective, target_selector: selector, tick: number|$variable)
    ```
    Set entity's score to start the timer.
    """
    def call(self) -> str:
        if self.raw_args["tick"].arg_type == ArgType.integer:
            return f'scoreboard players set {self.args["target_selector"]} {self.args["objective"]} {self.args["tick"]}'
        else:
            return f'scoreboard players operations {self.args["target_selector"]} {self.args["objective"]} = {self.args["tick"]}'


def points_to_commands(points: list[tuple[float, float, float]], particle: str, speed: str, count: str, mode: str) -> list[str]:
    commands = []
    for x_pos, y_pos, z_pos in points:
        commands.append(
            f'particle {particle} ^{x_pos:.10f} ^{y_pos:.10f} ^{z_pos:.10f} 0 0 0 {speed} {count} {mode}')
    return commands


@func_property(
    func_type=FuncType.jmc_command,
    call_string='Particle.circle',
    arg_type={
        "particle": ArgType.string,
        "radius": ArgType.integer,
        "spread": ArgType.integer,
        "speed": ArgType.integer,
        "count": ArgType.integer,
        "mode": ArgType.keyword,
    },
    name='particle_circle',
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    }
)
class ParticleCircle(JMCFunction):
    def draw(self, radius: int, spread: int) -> list[tuple[float, float, float]]:
        points = []
        angle = 2*math.pi/spread
        for i in drange(0, spread, angle):
            points.append((radius*math.cos(i), 0.0, radius*math.sin(i)))
        return points

    def call(self) -> str:
        if self.args['mode'] not in {'force', 'normal'}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    int(self.args["radius"]),
                    int(self.args["spread"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.jmc_command,
    call_string='Particle.spiral',
    arg_type={
        "particle": ArgType.string,
        "radius": ArgType.integer,
        "height": ArgType.integer,
        "spread": ArgType.integer,
        "speed": ArgType.integer,
        "count": ArgType.integer,
        "mode": ArgType.keyword,
    },
    name='particle_spiral',
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    }
)
class ParticleSpiral(JMCFunction):
    def draw(self, radius: int, height: int, spread: int) -> list[tuple[float, float, float]]:
        points = []
        angle = 2*math.pi/spread
        d_y = height/spread
        for i in range(spread):
            points.append((
                radius*math.cos(i*angle),
                i*d_y,
                radius*math.sin(i*angle)))
        return points

    def call(self) -> str:
        if self.args['mode'] not in {'force', 'normal'}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    int(self.args["radius"]),
                    int(self.args["height"]),
                    int(self.args["spread"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )


@func_property(
    func_type=FuncType.jmc_command,
    call_string='Particle.cylinder',
    arg_type={
        "particle": ArgType.string,
        "radius": ArgType.integer,
        "height": ArgType.integer,
        "spread_xz": ArgType.integer,
        "spread_y": ArgType.integer,
        "speed": ArgType.integer,
        "count": ArgType.integer,
        "mode": ArgType.keyword,
    },
    name='particle_cylinder',
    defaults={
        "speed": "1",
        "count": "1",
        "mode": "normal",
    }
)
class ParticleCylinder(JMCFunction):
    def draw(self, radius: int, height: int, spread_xz: int, spread_y: int) -> list[tuple[float, float, float]]:
        points = []
        d_y = height/spread_y
        for y in range(spread_y):
            angle = 2*math.pi/spread_xz
            for i in drange(0, spread_xz, angle):
                points.append((radius*math.cos(i), y*d_y, radius*math.sin(i)))
        return points

    def call(self) -> str:
        if self.args['mode'] not in {'force', 'normal'}:
            raise JMCSyntaxException(
                f"Unrecognized mode, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.raw_args["mode"].token, self.tokenizer)

        return self.datapack.add_raw_private_function(
            self.name,
            commands=points_to_commands(
                self.draw(
                    int(self.args["radius"]),
                    int(self.args["height"]),
                    int(self.args["spread_xz"]),
                    int(self.args["spread_y"])),
                self.args["particle"],
                self.args["speed"],
                self.args["count"],
                self.args["mode"]
            ),
        )
