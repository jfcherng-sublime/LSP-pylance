from .consts import SERVER_BINARY_PATH, SERVER_VERSION
from .helpers.dotted import Dottedable, create_dottable, dotted_get, dotted_set
from .helpers.plugin_message import status_msg
from .helpers.settings import get_setting
from .helpers.utils import unique
from .helpers.vs_marketplace_lsp_utils import VsMarketplaceClientHandler
from .helpers.vs_marketplace_lsp_utils import notification_handler
from .helpers.vs_marketplace_lsp_utils.vscode_settings import configure_lsp_like_vscode
from LSP.plugin import __version__ as lsp_version
from LSP.plugin.core.types import DottedDict
from typing import Any, Dict, List, Tuple
import os
import sublime
import sys


def plugin_loaded() -> None:
    configure_lsp_like_vscode()
    LspPylancePlugin.setup()


def plugin_unloaded() -> None:
    # the cleanup() will delete the downloaded server
    # we don't want this during developing this plugin...
    if not get_setting("developing"):
        LspPylancePlugin.cleanup()


class LspPylancePlugin(VsMarketplaceClientHandler):
    package_name = "LSP-pylance"

    # this InsiderChannel uid is dumped from Pylance 2020.11.2, extension.bundle.js
    extension_uid = "pylance-insiders.vscode-pylance"
    extension_version = SERVER_VERSION
    server_binary_path = SERVER_BINARY_PATH
    execute_with_node = True
    pretend_vscode = True

    # resources directories will be copied into the server directory during server installation
    resource_dirs = ["_resources"]

    # commands provided by the server (useless at this moment)
    supported_commands = [
        "pyright.addoptionalforparam",
        "pyright.createtypestub",
        "pyright.organizeimports",
        "python.addImport",
        "python.addOptionalForParam",
        "python.createTypeStub",
        "python.intellicode.completionItemSelected",
        "python.intellicode.loadLanguageServerExtension",
        "python.orderImports",
        "python.removeUnusedImport",
    ]

    key_extraPaths = "python.analysis.extraPaths"

    @classmethod
    def minimum_node_version(cls) -> Tuple[int, int, int]:
        return (12, 0, 0)

    @classmethod
    def download_from(cls) -> str:
        return "pvsc"

    def on_workspace_did_change_configuration(self, settings: DottedDict) -> None:
        super().on_workspace_did_change_configuration(settings)

        d = create_dottable(settings)

        if get_setting("dev_environment") == "sublime_text":
            self.inject_extra_paths_st(d, self.key_extraPaths)

    def on_workspace_configuration(self, params: Dict, configuration: Dict[str, Any]) -> None:
        super().on_workspace_configuration(params, configuration)

        d = create_dottable(configuration)
        section = params.get("section", "")

        if self.key_extraPaths.startswith(section) and get_setting("dev_environment") == "sublime_text":
            self.inject_extra_paths_st(d, self.key_extraPaths[len(section) :].lstrip("."))

    @classmethod
    def on_settings_read(cls, settings: sublime.Settings) -> bool:
        super().on_settings_read(settings)

        d = create_dottable(settings)

        if lsp_version < (1, 0, 0) and settings.get("dev_environment") == "sublime_text":  # type: ignore
            cls.inject_extra_paths_st(d, "settings." + cls.key_extraPaths)

        return False

    # -------- #
    # handlers #
    # -------- #

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
    def inject_extra_paths_st(cls, settings: Dottedable, key_extraPaths: str) -> None:
        extraPaths = dotted_get(settings, key_extraPaths, [])  # type: List[str]

        extraPaths.append("{}/_resources/typings".format(cls.server_directory_path() or "$server_directory_path"))
        extraPaths.extend(cls.find_package_dependency_dirs())
        extraPaths.append(sublime.installed_packages_path())

        dotted_set(settings, key_extraPaths, list(unique(extraPaths, stable=True)))

    @staticmethod
    def find_package_dependency_dirs() -> List[str]:
        dep_dirs = sys.path.copy()

        # move the "Packages/" to the last
        # @see https://github.com/sublimelsp/LSP-pyright/pull/26#discussion_r520747708
        packages_path = sublime.packages_path()
        dep_dirs.remove(packages_path)
        dep_dirs.append(packages_path)

        return [path for path in dep_dirs if os.path.isdir(path)]
