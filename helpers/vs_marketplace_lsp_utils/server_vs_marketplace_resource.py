from .typing import SemanticVersion
from .vscode_settings import VSCODE_CLIENTINFO
from LSP.plugin.core.typing import Dict, List, Optional
from lsp_utils import ServerResourceInterface
from lsp_utils import ServerStatus
from lsp_utils.helpers import log_and_show_message
from lsp_utils.helpers import parse_version
from lsp_utils.helpers import run_command_sync
from lsp_utils.helpers import version_to_string
from lsp_utils.server_npm_resource import NodeVersionResolver
from sublime_lib import ResourcePath
import gzip
import io
import os
import re
import shutil
import sublime
import urllib.error
import urllib.request
import zipfile

__all__ = [
    "DOWNLOAD_FROM_MARKETPLACE",
    "DOWNLOAD_FROM_PVSC",
    "ServerVsMarketplaceResource",
]


DOWNLOAD_FROM_MARKETPLACE = "marketplace"
DOWNLOAD_FROM_PVSC = "pvsc"


class NodeVersionResolver:
    """
    A singleton for resolving Node version once per session.
    """

    def __init__(self) -> None:
        self._version = None  # type: Optional[SemanticVersion]

    def resolve(self) -> Optional[SemanticVersion]:
        if self._version:
            return self._version
        version, error = run_command_sync(["node", "--version"])
        if error is not None:
            log_and_show_message("lsp_utils(NodeVersionResolver): Error resolving node version: {}!".format(error))
        else:
            self._version = parse_version(version)
        return self._version


node_version_resolver = NodeVersionResolver()


class ServerVsMarketplaceResource(ServerResourceInterface):
    """Global object providing paths to server resources.
    Also handles the installing and updating of the server in cache.

    setup() needs to be called during (or after) plugin_loaded() for paths to be valid.

    For example, for https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
    - extension_uid = "ms-python.vscode-pylance"
    - extension_version = "2020.11.1"
    """

    templates = {
        # the "marketplace" API has ratelimit...
        "marketplace": {
            "download": "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{vendor}/vsextensions/{name}/{version}/vspackage",
            "referer": "https://marketplace.visualstudio.com/items?itemName={vendor}.{name}",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        },
        # come from Pylance's obfuscated extension.bundle.js
        "pvsc": {
            "download": "https://pvsc.blob.core.windows.net/{vendor}/{name}-{version}.vsix",
            "referer": "",
            "user_agent": "VSCode " + VSCODE_CLIENTINFO["version"],
        },
    }

    # --------------------------- #
    # ServerVsMarketplaceResource #
    # --------------------------- #

    def __init__(
        self,
        package_name: str,
        extension_uid: str,
        extension_version: str,
        server_binary_path: str,
        package_storage: str,
        node_version: Optional[str],
        download_from: str = DOWNLOAD_FROM_MARKETPLACE,
        resource_dirs: List[str] = [],
    ) -> None:
        if not (package_name and extension_uid and extension_version and server_binary_path and package_storage):
            raise Exception("ServerVsMarketplaceResource could not initialize due to wrong input")

        self._package_name = package_name
        self._extension_uid = extension_uid
        self._extension_version = extension_version
        self._binary_path = server_binary_path
        self._package_storage = package_storage
        self._node_version = node_version
        self._download_place = download_from
        self._resource_dirs = resource_dirs.copy()

        # internal
        self._status = ServerStatus.UNINITIALIZED

    @property
    def server_directory_path(self) -> str:
        """ Looks like ".../Package Storage/LSP-pylance/ms-python.vscode-pylance~2020.11.1" """

        return os.path.join(self._package_storage, "{}~{}".format(self._extension_uid, self._extension_version))

    def _install_or_update(self) -> None:
        os.makedirs(self.server_directory_path, exist_ok=True)

        try:
            # copy resources before downloading the server so it may use those resources
            self._copy_resource_dirs()
            self._download_extension()
        except Exception as e:
            self._status = ServerStatus.ERROR
            raise e

        self._status = ServerStatus.READY

    def _copy_resource_dirs(self) -> None:
        try:
            for folder in self._resource_dirs:
                folder = re.sub(r"[\\/]+", "/", folder).strip("\\/")

                if not folder:
                    continue

                dir_src = "Packages/{}/{}/".format(self._package_name, folder)
                dir_dst = "{}/{}/".format(self.server_directory_path, folder)

                shutil.rmtree(dir_dst, ignore_errors=True)
                ResourcePath(dir_src).copytree(dir_dst, exist_ok=True)  # type: ignore
        except IOError:
            raise RuntimeError("Failed to copy resource files...")

    def _download_extension(self, save_vsix: bool = True) -> None:
        url = self._expaned_templates(self._download_place + ".download") or ""

        try:
            req = urllib.request.Request(
                url=url,
                headers={
                    "Accept-Encoding": "gzip, deflate",
                    "Referer": self._expaned_templates(self._download_place + ".referer") or "",
                    "User-Agent": self._expaned_templates(self._download_place + ".user_agent") or "",
                },
            )

            with urllib.request.urlopen(req) as resp:
                resp_data = resp.read()
                if resp.info().get("Content-Encoding") == "gzip":
                    resp_data = gzip.decompress(resp_data)
        except urllib.error.HTTPError as e:
            raise RuntimeError('Unable to download the extension from "{}" (HTTP code: {})'.format(url, e.code))
        except urllib.error.ContentTooShortError:
            raise RuntimeError("Extension was downloaded imcompletely...")

        if save_vsix:
            with io.open(os.path.join(self.server_directory_path, "extension.vsix"), "wb") as f:
                f.write(resp_data)

        with zipfile.ZipFile(io.BytesIO(resp_data), "r") as f:
            f.extractall(self.server_directory_path)

        if not os.path.isfile(self.binary_path):
            raise RuntimeError("Preparation done but somehow the server binary path is not a file.")

    def _expaned_templates(self, dotted: str, default: Optional[str] = None) -> Optional[str]:
        extension_vendor, extension_name = self._extension_uid.split(".")[:2]

        keys = dotted.split(".")
        ret = self.templates

        try:
            for key in keys:
                ret = ret[key]
        except KeyError:
            return default

        if not isinstance(ret, str):
            return default

        return ret.format_map(  # type: ignore
            {
                "name": extension_name,
                "vendor": extension_vendor,
                "version": self._extension_version,
            }
        )

    # ----------------------- #
    # ServerResourceInterface #
    # ----------------------- #

    @classmethod
    def create(cls, options: Dict) -> Optional["ServerVsMarketplaceResource"]:
        package_name = options["package_name"]  # type: str
        extension_uid = options["extension_uid"]  # type: str
        extension_version = options["extension_version"]  # type: str
        server_binary_path = options["server_binary_path"]  # type: str
        package_storage = options["package_storage"]  # type: str
        minimum_node_version = options["minimum_node_version"]  # type: Optional[SemanticVersion]
        download_from = options["download_from"] or DOWNLOAD_FROM_MARKETPLACE  # type: str
        resource_dirs = options["resource_dirs"] or []  # type: List[str]

        if minimum_node_version:
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
        else:
            installed_node_version = None

        return ServerVsMarketplaceResource(
            package_name,
            extension_uid,
            extension_version,
            server_binary_path,
            package_storage,
            version_to_string(installed_node_version) if installed_node_version else None,
            download_from,
            resource_dirs,
        )

    @property
    def binary_path(self) -> str:
        """ Looks like ".../Package Storage/LSP-pylance/ms-python.vscode-pylance~2020.11.1/extension/dist/server.bundle.js" """

        return os.path.join(self.server_directory_path, self._binary_path)

    def get_status(self) -> int:
        return self._status

    def needs_installation(self) -> bool:
        is_installed = os.path.isfile(self.binary_path)

        if is_installed:
            self._status = ServerStatus.READY
            return False

        return True

    def install_or_update(self, async_io: bool = False) -> None:
        shutil.rmtree(self.server_directory_path, ignore_errors=True)

        install_message = "{}: Installing server in path: {}".format(self._package_name, self.server_directory_path)
        log_and_show_message(install_message, show_in_status=False)

        if async_io:
            sublime.set_timeout_async(lambda: self._install_or_update(), 0)
        else:
            self._install_or_update()
