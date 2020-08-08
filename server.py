import os
import shutil
import sublime

from functools import lru_cache

from .const import PLUGIN_NAME, SETTINGS_FILENAME, SERVER_VERSION
from LSP.plugin.core.typing import Optional


@lru_cache()
def get_plugin_cache_dir() -> str:
    """
    @brief Get this plugin's cache dir.

    @return The cache dir.
    """

    return os.path.join(sublime.cache_path(), PLUGIN_NAME)


@lru_cache()
def get_server_download_url(version: str, arch: str, platform: str) -> Optional[str]:
    """
    @brief Get the LSP server download URL.

    @param version  The LSP server version
    @param arch     The arch ("x32" or "x64")
    @param platform The platform ("osx", "linux" or "windows")

    @return The LSP server download URL.
    """

    settings = sublime.load_settings(SETTINGS_FILENAME)
    url = settings.get("lsp_server_download_url", "")  # type: str

    return url.format_map({"version": version})


@lru_cache()
def get_server_dir() -> str:
    """
    @brief Get the LSP server dir.

    @return The LSP server dir.
    """

    return os.path.join(get_plugin_cache_dir(), SERVER_VERSION)


@lru_cache()
def get_server_bin_path() -> str:
    """
    @brief Get the LSP server binary path.

    @return The LSP server binary path.
    """

    return os.path.join(get_server_dir(), "extension", "server", "server.bundle.js")
