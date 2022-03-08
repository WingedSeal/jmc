from pathlib import Path
from .exception import JMCFileNotFoundError


def compile(config: dict) -> None:
    try:
        with Path(config["target"]).open('r') as target_file:
            raw_string = target_file.read()
    except FileNotFoundError:
        raise JMCFileNotFoundError(f"Main Target file not found: {config['target']}")
