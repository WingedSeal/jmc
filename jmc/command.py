import re
from typing import Set
from . import Logger, LoadJson
import logging

logger = Logger(__name__, logging.DEBUG)


class Command:
    def __init__(self, text: str, load_json: LoadJson) -> None:
        custom_command = re.match(r'^(\$\w+) = ([-+]?[0-9]+)$')
        if custom_command is None:
            self.text = text
            return
        load_json.scoreboards.add('variable')
        groups = custom_command.groups()
        self.text = f'scoreboard players set {groups[0]} variable {int(groups[1])}'

    def __str__(self) -> str:
        return self.text
