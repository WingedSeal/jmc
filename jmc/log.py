import logging
from datetime import datetime
from pathlib import Path

FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

__now = datetime.now()
FILE_PATH = Path(
    f'logs/{__now.strftime("%Y-%b")}/{__now.day}{__now.strftime("-%m-%Y")}.log')


def Logger(name: str, level: int = logging.DEBUG, file_path: str = None, is_stream: bool = True, is_log_file: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if is_log_file:
        if file_path is None:
            file_path = FILE_PATH
        else:
            file_path = Path(file_path)
        file_path: Path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path.resolve())
        file_handler.setFormatter(FORMATTER)
        logger.addHandler(file_handler)
    if is_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(FORMATTER)
        logger.addHandler(stream_handler)

    return logger
