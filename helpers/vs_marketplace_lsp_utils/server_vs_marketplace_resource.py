from LSP.plugin.core.typing import List, Optional
from lsp_utils.helpers import log_and_show_message
from lsp_utils.helpers import SemanticVersion
from lsp_utils.helpers import version_to_string
from lsp_utils.server_npm_resource import NodeVersionResolver
from sublime_lib import ActivityIndicator, ResourcePath
import gzip
import io
import os
import re
import shutil
import sublime
import urllib.error
import urllib.request
import zipfile


def get_server_vs_marketplace_resource_for_package(
    package_name: str,
    extension_uid: str,
    extension_version: str,
    server_binary_path: str,
    package_storage: str,
    minimum_node_version: SemanticVersion,
    resource_dirs: List[str] = [],
) -> Optional["ServerVsMarketplaceResource"]:
    if shutil.which("node") is None:
        log_and_show_message(
            "{}: Error: Node binary not found on the PATH."
            "Check the LSP Troubleshooting section for information on how to fix that: "
            "https://lsp.readthedocs.io/en/latest/troubleshooting/".format(package_name)
        )
        return None
    installed_node_version = node_version_resolver.resolve()
    if not installed_node_version:
        return None
    if installed_node_version < minimum_node_version:
        error = "Installed node version ({}) is lower than required version ({})".format(
            version_to_string(installed_node_version),
            version_to_string(minimum_node_version),
        )
        log_and_show_message("{}: Error:".format(package_name), error)
        return None
    return ServerVsMarketplaceResource(
        package_name,
        extension_uid,
        extension_version,
        server_binary_path,
        package_storage,
        version_to_string(installed_node_version),
        resource_dirs,
    )


node_version_resolver = NodeVersionResolver()


class ServerVsMarketplaceResource:
    """Global object providing paths to server resources.
    Also handles the installing and updating of the server in cache.

    setup() needs to be called during (or after) plugin_loaded() for paths to be valid.

    For example, for https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
    - extension_uid = "ms-python.vscode-pylance"
    - extension_version = "2020.10.1"
    """

    extension_urls = {
        "download": "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{vendor}/vsextensions/{name}/{version}/vspackage",
        "referer": "https://marketplace.visualstudio.com/items?itemName={vendor}.{name}",
    }

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36 Edg/86.0.622.63"

    def __init__(
        self,
        package_name: str,
        extension_uid: str,
        extension_version: str,
        server_binary_path: str,
        package_storage: str,
        node_version: str,
        resource_dirs: List[str] = [],
    ) -> None:
        self._initialized = False
        self._is_ready = False
        self._error_on_install = False
        self._package_name = package_name
        self._extension_uid = extension_uid
        self._extension_version = extension_version
        self._binary_path = server_binary_path
        self._package_storage = package_storage
        self._node_version = node_version
        self._resource_dirs = resource_dirs.copy()
        self._activity_indicator = None

        if not (self._package_name and self._extension_uid and self._extension_version and self._binary_path):
            raise Exception("ServerVsMarketplaceResource could not initialize due to wrong input")

    @property
    def ready(self) -> bool:
        return self._is_ready

    @property
    def error_on_install(self) -> bool:
        return self._error_on_install

    @property
    def binary_path(self) -> str:
        """ Looks like ".../Package Storage/LSP-pylance/ms-python.vscode-pylance~2020.11.1/extension/dist/server.bundle.js" """

        return os.path.join(self.server_directory, self._binary_path)

    @property
    def server_directory(self) -> str:
        """ Looks like ".../Package Storage/LSP-pylance/ms-python.vscode-pylance~2020.11.1" """

        return os.path.join(self._package_storage, "{}~{}".format(self._extension_uid, self._extension_version))

    def needs_installation(self) -> bool:
        if self._initialized:
            return False

        is_installed = os.path.isfile(self.binary_path)

        self._initialized = True
        self._is_ready = is_installed

        return not is_installed

    def install_or_update(self, async_io: bool) -> None:
        shutil.rmtree(self.server_directory, ignore_errors=True)

        install_message = "{}: Installing server in path: {}".format(self._package_name, self.server_directory)
        log_and_show_message(install_message, show_in_status=False)

        active_window = sublime.active_window()
        active_view = active_window.active_view()
        if active_window and active_view:
            self._activity_indicator = ActivityIndicator(active_view, install_message)  # type: ignore
            self._activity_indicator.start()

        if async_io:
            sublime.set_timeout_async(lambda: self._install_or_update(), 0)
        else:
            self._install_or_update()

    def _on_install_success(self, _: str) -> None:
        self._is_ready = True
        self._stop_indicator()
        log_and_show_message("{}: Server installed. Sublime Text restart might be required.".format(self._package_name))

    def _on_error(self, error: str) -> None:
        self._error_on_install = True
        self._stop_indicator()
        log_and_show_message("{}: Error:".format(self._package_name), error)

    def _stop_indicator(self) -> None:
        if self._activity_indicator:
            self._activity_indicator.stop()
            self._activity_indicator = None

    # -------------- #
    # custom methods #
    # -------------- #

    def _install_or_update(self) -> None:
        # copy resources before downloading the server so it may use those resources
        self._copy_resource_dirs()
        self._download_extension()

    def _copy_resource_dirs(self) -> None:
        for folder in self._resource_dirs:
            folder = re.sub(r"[\\/]+", "/", folder).strip("\\/")

            dir_src = "Packages/{}/{}/".format(self._package_name, folder)
            dir_dst = "{}/{}/".format(self.server_directory, folder)

            shutil.rmtree(dir_dst, ignore_errors=True)
            ResourcePath(dir_src).copytree(dir_dst, exist_ok=True)  # type: ignore

    def _download_extension(self) -> None:
        try:
            req = urllib.request.Request(
                url=self._get_expaneded_url("download"),
                headers={
                    "Accept-Encoding": "gzip, deflate",
                    "Referer": self._get_expaneded_url("referer"),
                    "User-Agent": self.user_agent,
                },
            )

            with urllib.request.urlopen(req) as resp:
                resp_data = resp.read()
                if resp.info().get("Content-Encoding") == "gzip":
                    resp_data = gzip.decompress(resp_data)
        except urllib.error.HTTPError as e:
            self._on_error("Unable to download the extension (HTTP code: {})".format(e.code))
            return
        except urllib.error.ContentTooShortError as e:
            self._on_error("Extension was downloaded imcompletely...")
            return

        vsix_path = os.path.join(self.server_directory, "extension.vsix")
        os.makedirs(os.path.dirname(vsix_path), exist_ok=True)
        with io.open(vsix_path, "wb") as f:
            f.write(resp_data)
        self._decompress_vsix(vsix_path)

        if os.path.isfile(self.binary_path):
            self._on_install_success("")
        else:
            self._on_error("Preparation done but somehow the server binary path is not a file.")

    @staticmethod
    def _decompress_vsix(file: str, dst_dir: Optional[str] = None) -> None:
        """
        @brief Decompress the .vsix (ZIP) tarball.

        @param file    The .vsix tarball
        @param dst_dir The destination directory
        """

        if not dst_dir:
            dst_dir = os.path.dirname(file)

        with zipfile.ZipFile(file) as f:
            f.extractall(dst_dir)

    def _get_expaneded_url(self, item: str) -> str:
        extension_vendor, extension_name = self._extension_uid.split(".")[:2]

        return self.extension_urls[item].format_map(
            {
                "name": extension_name,
                "vendor": extension_vendor,
                "version": self._extension_version,
            }
        )
