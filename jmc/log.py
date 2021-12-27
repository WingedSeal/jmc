import logging
from datetime import datetime
from pathlib import Path

FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')


def Logger(name: str, level: int, file_path: str = None, is_stream: bool = True, is_log_file: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if is_log_file:
        if file_path is None:
            now = datetime.now()
            file_path = Path(
                f'logs/{now.strftime("%Y-%b")}/{now.day}{now.strftime("-%m-%Y")}.log')
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

    # Override level
    logger.setLevel(logging.DEBUG)

    return logger
