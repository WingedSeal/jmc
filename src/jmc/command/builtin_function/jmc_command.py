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


@func_property(
    func_type=FuncType.jmc_command,
    call_string='Particle.display',
    arg_type={
        "particle": ArgType.string,
        "shape": ArgType.string,
        "size": ArgType.integer,
        "spread": ArgType.integer,
        "speed": ArgType.integer,
        "count": ArgType.integer,
        "mode": ArgType.keyword,
        "height": ArgType.integer
    },
    name='particle_display',
    defaults={
        "speed": 1,
        "count": 1,
        "mode": "normal",
        "height": 0,
    }
)
class ParticleDisplay(JMCFunction):
    def points_to_commands(self, points: list[tuple[int, int]], particle: str, speed: int, count: int, mode: str) -> list[str]:
        commands = []
        for x_pos, y_pos, z_pos in points:
            commands.append(
                f'particle {particle} ^{x_pos:.10f} ^{y_pos:.10f} ^{z_pos:.10f} 0 0 0 {speed} {count} {mode}')
        return commands

    def draw(self, shape: str, size: int, spread: int, height: int) -> list[tuple[int, int]]:
        if height is not None:
            height = int(height)
        points = []
        if shape == "circle":
            if height is not None:
                raise JMCSyntaxException(
                    f"'circle' shape does not support height", self.args_Args["height"].token, self.tokenizer)
            angle = 2*math.pi/spread
            for i in drange(0, spread, angle):
                points.append((size*math.cos(i), 0, size*math.sin(i)))
            return points

        if shape == "spiral":
            angle = 2*math.pi/spread
            d_y = height/spread
            for i in range(spread):
                points.append((
                    size*math.cos(i*angle),
                    i*d_y,
                    size*math.sin(i*angle)))
            return points

    def call(self) -> str:
        if self.args['mode'] not in {'force', 'normal'}:
            raise JMCSyntaxException(
                f"Unrecognized shape, '{self.args['mode']}' Available modes are 'force' and 'normal'", self.args_Args["mode"].token, self.tokenizer)
        if self.args["shape"] in {"circle", "spiral"}:
            return self.datapack.add_raw_private_function(
                self.name,
                commands=self.points_to_commands(
                    self.draw(
                        self.args["shape"],
                        int(self.args["size"]),
                        int(self.args["spread"]),
                        int(self.args["height"])),
                    self.args["particle"],
                    self.args["speed"],
                    self.args["count"],
                    self.args["mode"]
                ),
            )
        raise JMCSyntaxException(
            f"Unrecognized shape, '{self.args['shape']}'", self.args_Args["shape"].token, self.tokenizer)
