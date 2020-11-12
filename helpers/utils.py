import sublime

from typing import Any, Optional


def dotted_get(var: Any, dotted: str, default: Optional[Any] = None) -> Any:
    """
    @brief Get the value from the variable with dotted notation.

    @param var     The variable
    @param dotted  The dotted
    @param default The default

    @return The value or the default if dotted not found
    """

    keys = dotted.split(".")

    try:
        for key in keys:
            if isinstance(var, sublime.Settings):
                var = var.get(key, default)
            elif isinstance(var, dict):
                var = var.get(key)
            elif isinstance(var, (list, tuple, bytes, bytearray)):
                var = var[int(key)]
            else:
                var = getattr(var, key)

        return var
    except Exception:
        return default


def dotted_set(var: Any, dotted: str, value: Any) -> None:
    """
    @brief Set the value for the variable with dotted notation.

    @param var     The variable
    @param dotted  The dotted
    @param default The default
    """

    keys = dotted.split(".")
    last_key = keys.pop()

    for key in keys:
        if isinstance(var, (dict, sublime.Settings)):
            var = var.get(key)
        elif isinstance(var, (list, tuple, bytes, bytearray)):
            var = var[int(key)]
        else:
            var = getattr(var, key)

    if isinstance(var, (dict, sublime.Settings)):
        var[last_key] = value  # type: ignore
    elif isinstance(var, (list, tuple, bytes, bytearray)):
        var[int(last_key)] = value  # type: ignore
    else:
        setattr(var, last_key, value)
