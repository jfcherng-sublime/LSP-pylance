from LSP.plugin.core.typing import Any, Callable, Dict, Iterable, Union


# the first argument is always "self"
T_NOTIFICATION_HANDLER = Callable[[Any, Dict[str, Any]], None]
T_REQUEST_HANDLER = Callable[[Any, Dict[str, Any]], None]

HANDLER_MARK_NOTIFICATION = "__event_names_notification"
HANDLER_MARK_REQUEST = "__event_names_request"


def as_notification_handler(
    event_names: Union[str, Iterable[str]]
) -> Callable[[T_NOTIFICATION_HANDLER], T_NOTIFICATION_HANDLER]:
    """ Marks the decorated function as a handler for the notification event. """

    event_names = [event_names] if isinstance(event_names, str) else list(event_names)

    def decorator(func: T_NOTIFICATION_HANDLER) -> T_NOTIFICATION_HANDLER:
        setattr(func, HANDLER_MARK_NOTIFICATION, event_names)
        return func

    return decorator


def as_request_handler(event_names: Union[str, Iterable[str]]) -> Callable[[T_REQUEST_HANDLER], T_REQUEST_HANDLER]:
    """ Marks the decorated function as a handler for the request event. """

    event_names = [event_names] if isinstance(event_names, str) else list(event_names)

    def decorator(func: T_REQUEST_HANDLER) -> T_REQUEST_HANDLER:
        setattr(func, HANDLER_MARK_REQUEST, event_names)
        return func

    return decorator
