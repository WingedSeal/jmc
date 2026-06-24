from typing import Callable

_message_handler: Callable[[str], None] = print


def register_message(fn: Callable[[str], None]) -> None:
    """Register a handler for user-facing compile-time messages.

    This hook avoids a circular import and prevents the compile module from knowing specifics of how output is rendered.
    Note: Must be called before compilation begins. Not thread-safe to call concurrently with emit_message.

    :param fn: lambda which receives the message string and renders it.
    """
    global _message_handler
    _message_handler = fn


def emit_message(message: str) -> None:
    """Emit a user-facing message through the registered handler.

    :param message: The message string to emit.
    """
    _message_handler(message)
