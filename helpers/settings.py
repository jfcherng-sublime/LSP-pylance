from .dotted import dotted_get
from functools import lru_cache
from typing import Any, Optional
import os
import sublime


def get_package_name() -> str:
    """ Gets the package name. """

    # __package__ will be in the form of "PLUGIN_NAME.xxx.yyy..."
    # bug anyway, the top module should always be the plugin name
    return __package__.split(".")[0]


@lru_cache()
def get_package_path(package_name: Optional[str] = None, full_path: bool = False) -> str:
    """
    Gets the package directory path.

    :param      package_name:  The package name
    :param      full_path:     Returns full path, otherwise "Packages/..."

    :returns:   The package directory path.
    """

    return os.path.join(
        sublime.packages_path() if full_path else "Packages",
        package_name or get_package_name(),
    )


@lru_cache()
def get_settings_object(package_name: Optional[str] = None) -> sublime.Settings:
    """ Gets the settings object. """

    return sublime.load_settings((package_name or get_package_name()) + ".sublime-settings")


def get_setting(dotted: str, default: Optional[Any] = None, package_name: Optional[str] = None) -> Any:
    """
    Gets the plugin setting with the dotted key.

    :param      dotted:        The dotted key
    :param      default:       The default value if the key doesn't exist
    :param      package_name:  The package name, the current package if not provided

    :returns:   The setting's value.
    """

    return dotted_get(get_settings_object(package_name), dotted, default)
