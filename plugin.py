from .consts import EXTENSION_UID
from .consts import EXTENSION_VERSION
from .consts import SERVER_BINARY_PATH
from .dev import vscode_env
from .dev import vscode_python_settings
from .helpers.plugin_message import status_msg
from .helpers.utils import unique
from .helpers.vs_marketplace_lsp_utils import configure_lsp_like_vscode
from .helpers.vs_marketplace_lsp_utils import DOWNLOAD_FROM_PVSC
from .helpers.vs_marketplace_lsp_utils import VsMarketplaceClientHandler
from LSP.plugin import ClientConfig
from LSP.plugin import DottedDict
from LSP.plugin import WorkspaceFolder
from LSP.plugin.core.typing import Any, Dict, List, Optional
from lsp_utils import notification_handler
import os
import sublime
import sys


def plugin_loaded() -> None:
    configure_lsp_like_vscode()
    LspPylancePlugin.setup()


def plugin_unloaded() -> None:
    # the cleanup() will delete the downloaded server
    # we don't want this during developing this plugin...
    if not LspPylancePlugin.get_plugin_setting("developing"):
        LspPylancePlugin.cleanup()


class LspPylancePlugin(VsMarketplaceClientHandler):
    package_name = __package__.split(".")[0]

    extension_uid = EXTENSION_UID
    extension_version = EXTENSION_VERSION
    server_binary_path = SERVER_BINARY_PATH
    execute_with_node = True
    pretend_vscode = True
    download_from = DOWNLOAD_FROM_PVSC

    # resources directories will be copied into the server directory during server installation
    resource_dirs = ["_resources"]

    def on_settings_changed(self, settings: DottedDict) -> None:
        super().on_settings_changed(settings)

        if self.get_plugin_setting("dev_environment") == "sublime_text":
            # add package dependencies into "python.analysis.extraPaths"
            extraPaths = settings.get("python.analysis.extraPaths") or []  # type: List[str]
            extraPaths.extend(self.find_package_dependency_dirs())
            extraPaths.append("${server_directory_path}/_resources/typings")
            settings.set("python.analysis.extraPaths", list(unique(extraPaths, stable=True)))

        if self.get_plugin_setting("developing"):
            vscpy_settings = DottedDict(vscode_python_settings())
            vscpy_settings.update(settings.get())
            settings.assign(vscpy_settings.get())

    @classmethod
    def on_pre_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List[WorkspaceFolder],
        configuration: ClientConfig,
    ) -> Optional[str]:
        super().on_pre_start(window, initiating_view, workspace_folders, configuration)

        if cls.get_plugin_setting("developing"):
            env = getattr(configuration, "env")  # type: Dict[str, str]
            env.update(vscode_env())

    # ---------------- #
    # message handlers #
    # ---------------- #

    @notification_handler("telemetry/event")
    def nh_telemetry_event(self, params: Dict[str, Any]) -> None:
        """ Handles notification event: `telemetry/event` """

        event_name = params.get("EventName", "")
        measurements = params.get("Measurements", {})

        if event_name == "language_server/analysis_complete" and measurements.get("numFilesAnalyzed", -1) >= 0:
            return status_msg(
                "{_}: Analysis {file_counts} files completed in {time_s:.3f} seconds.{first_run}",
                file_counts="{numFilesAnalyzed}/{numFilesInProgram}".format_map(measurements),
                time_s=measurements.get("elapsedMs", 0) / 1000,
                first_run=" (first run)" if measurements.get("isFirstRun") else "",
            )

    @notification_handler("workspace/semanticTokens/refresh")
    def nh_workspace_semanticTokens_refresh(self, params: List[Any]) -> None:
        pass

    # -------------- #
    # custom methods #
    # -------------- #

    @classmethod
    def get_plugin_setting(cls, key: str, default: Optional[Any] = None) -> Any:
        return sublime.load_settings(cls.package_name + ".sublime-settings").get(key, default)

    @staticmethod
    def find_package_dependency_dirs() -> List[str]:
        dep_dirs = sys.path.copy()

        # move the "Packages/" to the last
        # @see https://github.com/sublimelsp/LSP-pyright/pull/26#discussion_r520747708
        packages_path = sublime.packages_path()
        dep_dirs.remove(packages_path)
        dep_dirs.append(packages_path)

        # just for laziness because sometimes I just decompress the package source there
        dep_dirs.append(sublime.installed_packages_path())

        return [path for path in dep_dirs if os.path.isdir(path)]
