import re
from . import Logger, LoadJson
import logging

logger = Logger(__name__, logging.DEBUG)


class Command:
    def __init__(self, text: str, load_json: LoadJson) -> None:
        custom_command = re.match(r'^(\$\w+) = ([-+]?[0-9]+)$', text)
        if custom_command is None:
            self.text = text
        else:
            load_json.scoreboards.add('variable')
            groups = custom_command.groups()
            self.text = f'scoreboard players set {groups[0]} variable {int(groups[1])}'
        logger.debug(f"""Command created: 
        Custom Command: {custom_command.group(0) if custom_command is not None else None}
        Text: {self.text}""")

    def __str__(self) -> str:
        return self.text
