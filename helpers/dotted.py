from abc import ABCMeta, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union
from LSP.plugin.core.types import DottedDict
import re
import sublime


try:
    from LSP.plugin.core.types import ResolvedStartupConfig
except ImportError:
    # LSP for ST 3 doesn't have ResolvedStartupConfig
    class ResolvedStartupConfig:
        pass


_T = TypeVar("_T")


class DottedUnreachableException(Exception):
    def __init__(self, dotted: str) -> None:
        super().__init__('Path "{}" is unreachable...'.format(dotted))


class Dottedable(Generic[_T], metaclass=ABCMeta):
    @abstractmethod
    def dotted_get(self, dotted: Optional[str], default: Optional[Any] = None) -> Any:
        pass

    @abstractmethod
    def dotted_set(self, dotted: str, value: Any) -> None:
        pass

    @property
    def wrapped(self) -> _T:
        return self._wrapped

    def __init__(self, wrapped: _T, *args, **kwargs) -> None:
        self._wrapped = wrapped

    def d2k(self, dotted: str) -> List[str]:
        """
        Converts the dotted string into keys.

        - `"a.b.c"` becomes `["a", "b", "c"]`
        - `"a.<b.c>.d"` becomes `["a", "b.c", "d"]`
        """

        return [m.group(1) or m.group(2) for m in re.finditer(r"([^.\[\]]+)|<([^>]+)>", dotted)]

    def k2d(self, keys: List[str]) -> str:
        """
        Converts keys into a dotted string.

        - `["a", "b", "c"]` becomes `"a.b.c"`
        - `["a", "b.c", "d"]` becomes `"a.<b.c>.d"`
        """

        return ".".join(map(lambda key: ("<" + key + ">" if "." in key else key), keys))


class DictWrapper(Dottedable[dict]):
    def dotted_get(self, dotted: Optional[str], default: Optional[Any] = None) -> Any:
        if not dotted:
            return self._wrapped

        return keys_get_native(self._wrapped, self.d2k(dotted), default)

    def dotted_set(self, dotted: str, value: Any) -> None:
        if not dotted:
            return None

        try:
            keys_set_native(self._wrapped, self.d2k(dotted), value)
        except Exception:
            raise DottedUnreachableException(dotted)


class SettingsWrapper(Dottedable[sublime.Settings]):
    def dotted_get(self, dotted: Optional[str], default: Optional[Any] = None) -> Any:
        if not dotted:
            return self._wrapped

        keys = self.d2k(dotted)
        top_key = keys.pop(0)

        if not self._wrapped.has(top_key):
            return default

        return keys_get_native(self._wrapped.get(top_key), keys, default)

    def dotted_set(self, dotted: str, value: Any) -> None:
        if not dotted:
            return None

        keys = self.d2k(dotted)
        top_key = keys.pop(0)

        if self._wrapped.has(top_key):
            top_item = self._wrapped.get(top_key)  # this is a copy
        else:
            if keys:
                raise DottedUnreachableException(dotted)

            top_item = value

        try:
            keys_set_native(top_item, keys, value)
        except Exception:
            raise DottedUnreachableException(dotted)

        self._wrapped.set(top_key, top_item)


class DottedDictWrapper(Dottedable[DottedDict]):
    def __init__(self, wrapped: DottedDict) -> None:
        super().__init__(wrapped)

        self.d = wrapped.get() or {}  # type: dict
        self._d = DictWrapper(self.d)

    def dotted_get(self, dotted: Optional[str], default: Optional[Any] = None) -> Any:
        return self._d.dotted_get(dotted, default)

    def dotted_set(self, dotted: str, value: Any) -> None:
        self._d.dotted_set(dotted, value)
        self._wrapped.assign(self.d)


class ResolvedStartupConfigWrapper(Dottedable[ResolvedStartupConfig]):
    def dotted_get(self, dotted: Optional[str], default: Optional[Any] = None) -> Any:
        if not dotted:
            return self._wrapped

        keys = self.d2k(dotted)
        top_key = keys.pop(0)

        if not hasattr(self._wrapped, top_key):
            # should not read custom attribute in ResolvedStartupConfig
            raise DottedUnreachableException(dotted)

        return keys_get_native(getattr(self._wrapped, top_key), keys, default)

    def dotted_set(self, dotted: str, value: Any) -> None:
        if not dotted:
            return None

        keys = self.d2k(dotted)
        top_key = keys.pop(0)

        if not hasattr(self._wrapped, top_key):
            # cannot create custom attribute in ResolvedStartupConfig
            raise DottedUnreachableException(dotted)

        top_item = value

        try:
            keys_set_native(top_item, keys, value)
        except Exception:
            raise DottedUnreachableException(dotted)

        setattr(self._wrapped, top_key, top_item)


def create_dottable(var: Any) -> Dottedable:
    if isinstance(var, Dottedable):
        return var

    if isinstance(var, dict):
        return DictWrapper(var)

    if isinstance(var, sublime.Settings):
        return SettingsWrapper(var)

    if isinstance(var, DottedDict):
        return DottedDictWrapper(var)

    if isinstance(var, ResolvedStartupConfig):
        return ResolvedStartupConfigWrapper(var)

    raise TypeError("Failed to wrap the variable into a Dottable.")


def dotted_get(var: Any, dotted: str, default: Optional[Any] = None) -> Any:
    """
    Gets the value from the variable with dotted notation.

    :param var:     The variable
    :param dotted:  The dotted
    :param default: The default

    :returns: The value or the default if dotted not found
    """

    return create_dottable(var).dotted_get(dotted, default)


def dotted_set(var: Any, dotted: str, value: Any) -> None:
    """
    Sets the value for the variable with dotted notation.

    :param var:    The variable
    :param dotted: The dotted
    :param value:  The value
    """

    create_dottable(var).dotted_set(dotted, value)


def keys_get_native(var: Union[dict, list, tuple], keys: List[str], default: Optional[Any]) -> Any:
    try:
        # should raise an exception if any key doesn'_t exist so returns the default
        for key in keys:
            if isinstance(var, dict):
                var = var[key]
            elif isinstance(var, (list, tuple)):
                var = var[int(key)]
            else:
                var = getattr(var, key)
    except Exception:
        return default

    return var


def keys_set_native(var: Union[dict, list, tuple], keys: List[str], value: Any) -> None:
    if not keys:
        return

    last_key = keys.pop()

    for key in keys:
        if isinstance(var, dict):
            var = var.setdefault(key, {})
        elif isinstance(var, (list, tuple)):
            var = var[int(key)]
        else:
            var = getattr(var, key)

    # handle the last key, assign the actual value
    if isinstance(var, dict):
        var[last_key] = value
    elif isinstance(var, (list, tuple)):
        var[int(last_key)] = value  # type: ignore
    else:
        raise RuntimeError()
