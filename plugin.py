import os
import requests
import shutil
import sublime

from .const import ARCH, PLATFORM, PLUGIN_NAME, SETTINGS_FILENAME, SERVER_VERSION
from .server import (
    get_plugin_cache_dir,
    get_server_bin_path,
    get_server_dir,
    get_server_download_url,
)
from .tarball import decompress
from LSP.plugin import AbstractPlugin
from LSP.plugin.core.protocol import WorkspaceFolder
from LSP.plugin.core.types import ClientConfig
from LSP.plugin.core.typing import Dict, List, Tuple, Optional


def plugin_loaded() -> None:
    pass


def plugin_unloaded() -> None:
    pass


class LspPylancePlugin(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return PLUGIN_NAME

    @classmethod
    def configuration(cls) -> Tuple[sublime.Settings, str]:
        settings_path = "Packages/{}/{}".format(PLUGIN_NAME, SETTINGS_FILENAME)
        settings = sublime.load_settings(SETTINGS_FILENAME)

        if not settings.get("command"):
            settings.set("command", ["node", get_server_bin_path(), "--stdio"])

        return settings, settings_path

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        variables = {}
        variables["sublime_py_files_dir"] = os.path.dirname(sublime.__file__)
        return variables

    @classmethod
    def can_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List[WorkspaceFolder],
        configuration: ClientConfig,
    ) -> Optional[str]:
        try:
            if not shutil.which("node"):
                raise RuntimeError("Please install Node.js for the server to work.")
        except Exception as e:
            return "{}: {}".format(PLUGIN_NAME, e)

        return None

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        return not os.path.isfile(get_server_bin_path())

    @classmethod
    def install_or_update(cls) -> None:
        cls.cleanup_cache()
        cls.prepare_server_bin()

    @classmethod
    def prepare_server_bin(cls) -> None:
        """ Prepare the LSP server binary """

        server_dir = get_server_dir()
        download_url = get_server_download_url(SERVER_VERSION, ARCH, PLATFORM)
        tarball_path = os.path.join(server_dir, "extension-{}.vsix".format(SERVER_VERSION))

        # download the LSP server tarball
        os.makedirs(os.path.dirname(tarball_path), exist_ok=True)
        response = requests.get(download_url, stream=True)
        with open(tarball_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        decompress(tarball_path, server_dir)

    @classmethod
    def cleanup_cache(cls) -> None:
        """ Clean up this plugin's cache directory """

        shutil.rmtree(get_plugin_cache_dir(), ignore_errors=True)
