from io import StringIO

log_stream = StringIO()


def get_log() -> str:
    """Return log string"""
    return log_stream.getvalue()
