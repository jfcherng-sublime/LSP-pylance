import re
import sublime

from typing import Any, Iterable, Iterator, List, Optional, TypeVar, Union

try:
    from LSP.plugin.core.types import DottedDict
except ImportError:

    class DottedDict:
        def get(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass


_T = TypeVar("_T")


def dotted_string_to_keys(dotted: str) -> List[str]:
    return [m.group(1) or m.group(2) for m in re.finditer(r"([^.\[\]]+)|\[([^\]]+)\]", dotted)]


def keys_to_dotted_string(keys: List[str]) -> str:
    return ".".join(map(lambda key: "[" + key + "]" if "." in key else key, keys))


def dotted_get(var: Any, dotted: str, default: Optional[Any] = None) -> Any:
    """
    @brief Get the value from the variable with dotted notation.

    @param var     The variable
    @param dotted  The dotted
    @param default The default

    @return The value or the default if dotted not found
    """

    keys = dotted_string_to_keys(dotted)

    try:
        for key in keys:
            if isinstance(var, sublime.Settings):
                key = keys.pop(0)

                if not var.has(key):
                    return default

                var = var.get(key)
            elif isinstance(var, DottedDict):
                var = var.get(key)
            elif isinstance(var, dict):
                var = var[key]
            elif isinstance(var, (list, tuple)):
                var = var[int(key)]
            else:
                var = getattr(var, key)

        return var
    except Exception:
        return default


def dotted_set(var: Any, dotted: str, value: Any) -> None:
    """
    @brief Set the value for the variable with dotted notation.

    @param var    The variable
    @param dotted The dotted
    @param value  The value
    """

    keys = dotted_string_to_keys(dotted)
    last_key = keys.pop()

    for idx, key in enumerate(keys):
        if isinstance(var, sublime.Settings):
            rest_keys = keys[idx:] + [last_key]
            dotted_set_settings(var, keys_to_dotted_string(rest_keys), value)
            return
        elif isinstance(var, (dict, DottedDict)):
            var = var.get(key)
        elif isinstance(var, (list, tuple)):
            var = var[int(key)]
        else:
            var = getattr(var, key)

    # handle the last key, assign the actual value
    if isinstance(var, sublime.Settings):
        dotted_set_settings(var, last_key, value)
    elif isinstance(var, DottedDict):
        var.set(last_key, value)
    elif isinstance(var, dict):
        var[last_key] = value
    elif isinstance(var, (list, tuple)):
        var[int(last_key)] = value  # type: ignore
    else:
        setattr(var, last_key, value)


def dotted_set_settings(settings: sublime.Settings, dotted: str, value: Any) -> None:
    """
    @brief Set the value for the sublime.Settings object with dotted notation.

    @param settings The sublime.Settings object
    @param dotted   The dotted
    @param value    The value
    """

    keys = dotted_string_to_keys(dotted)

    top_item = settings.get(keys[0])  # this is a copy, not reference
    sub_dotted = keys_to_dotted_string(keys[1:])

    if sub_dotted:
        dotted_set(top_item, sub_dotted, value)
    else:
        top_item = value

    settings.set(keys[0], top_item)


def unique(it: Iterable[_T], stable: bool = False) -> Iterator[_T]:
    """
    Generates a collection of unique items from the iterable.

    @param stable If True, returned items are garanteed to be in their original relative ordering.
    """

    from collections import OrderedDict

    return (OrderedDict.fromkeys(it).keys() if stable else set(it)).__iter__()


def get_command_name(var: Union[type, str]) -> str:
    name = var.__name__ if isinstance(var, type) else str(var)

    name = re.sub(r"Command$", "", name)
    name = re.sub(r"([A-Z])", r"_\1", name)
    name = re.sub(r"_{2,}", "_", name)

    return name.strip("_").lower()
