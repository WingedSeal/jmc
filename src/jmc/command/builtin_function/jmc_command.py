import math
from typing import Optional
from jmc.exception import JMCSyntaxException
from ..utils import ArgType
from ..jmc_function import JMCFunction, FuncType, func_property


def drange(start, stop, step):
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
    def call(self) -> str:
        if self.args_Args["tick"].arg_type == ArgType.integer:
            return f'scoreboard players set {self.args["target_selector"]} {self.args["objective"]} {self.args["tick"]}'
        else:
            return f'scoreboard players operations {self.args["target_selector"]} {self.args["objective"]} = {self.args["tick"]}'


def points_to_commands(points: list[tuple[int, int]], particle: str, speed: int, count: int, mode: str) -> list[str]:
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
        "speed": 1,
        "count": 1,
        "mode": "normal",
    }
)
class ParticleCircle(JMCFunction):
    def draw(self, radius: int, spread: int) -> list[tuple[int, int]]:
        points = []
        angle = 2*math.pi/spread
        for i in drange(0, spread, angle):
            points.append((radius*math.cos(i), 0, radius*math.sin(i)))
        return points

    def call(self) -> str:
        if self.args['mode'] not in {'force', 'normal'}:
            raise JMCSyntaxException(
                f"Unrecognized shape, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.args_Args["mode"].token, self.tokenizer)

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
        "speed": 1,
        "count": 1,
        "mode": "normal",
    }
)
class ParticleSpiral(JMCFunction):
    def draw(self, radius: int, height: int, spread: int) -> list[tuple[int, int]]:
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
                f"Unrecognized shape, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.args_Args["mode"].token, self.tokenizer)

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
