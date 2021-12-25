import logging

FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')


def Logger(name: str, level: int, file_path: str = "test.log", is_stream: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if file_path:
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(FORMATTER)
        logger.addHandler(file_handler)
    if is_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(FORMATTER)
        logger.addHandler(stream_handler)
    return logger
