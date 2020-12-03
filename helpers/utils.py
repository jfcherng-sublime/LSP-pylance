from typing import Iterable, Iterator, TypeVar, Union
import re

T = TypeVar("T")


def unique(it: Iterable[T], stable: bool = False) -> Iterator[T]:
    """
    Generates a collection of unique items from the iterable.

    :param      stable:  If True, returned items are garanteed in their original relative order.
    """

    from collections import OrderedDict

    return (OrderedDict.fromkeys(it).keys() if stable else set(it)).__iter__()


def get_command_name(var: Union[type, str]) -> str:
    """
    Gets the command name in Sublime Text.

    :param      var:  The variable
    """

    name = var.__name__ if isinstance(var, type) else str(var)

    name = re.sub(r"Command$", "", name)
    name = re.sub(r"([A-Z])", r"_\1", name)
    name = re.sub(r"_{2,}", "_", name)

    return name.strip("_").lower()
