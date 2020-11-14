import sys


from LSP.plugin.core.typing import Any, Callable

if sys.version_info >= (3, 8, 0):
    from typing import TypeVar
else:
    # TypeVar is not available in LSP for ST 3...
    def TypeVar(*args, **kwargs) -> Any:
        return object


_T = TypeVar("_T")


def as_notification_handler(event_name: str) -> Callable[[_T], _T]:
    """ Marks the decorated function as a handler for the notification event. """

    def decorator(func: _T) -> _T:
        setattr(func, "__notification_event_name", event_name)
        return func

    return decorator


def as_request_handler(event_name: str) -> Callable[[_T], _T]:
    """ Marks the decorated function as a handler for the request event. """

    def decorator(func: _T) -> _T:
        setattr(func, "__request_event_name", event_name)
        return func

    return decorator
