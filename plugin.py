import os
import sublime
import sys

from typing import Any, Dict, List, Tuple

from .consts import SERVER_BINARY_PATH, SERVER_VERSION
from .helpers.settings import get_setting
from .helpers.utils import dotted_get
from .helpers.vs_marketplace_lsp_utils import ApiWrapperInterface, VsMarketplaceClientHandler
from .helpers.vs_marketplace_lsp_utils.pretend_vscode import *


def plugin_loaded() -> None:
    LspPylancePlugin.setup()


def plugin_unloaded() -> None:
    # the cleanup() will delete the downloaded server
    # we don't want this during developing this plugin...
    if not get_setting("developing"):
        LspPylancePlugin.cleanup()


class LspPylancePlugin(VsMarketplaceClientHandler):
    package_name = "LSP-pylance"

    # @see https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
    extension_uid = "ms-python.vscode-pylance"
    extension_version = SERVER_VERSION
    server_binary_path = SERVER_BINARY_PATH
    execute_with_node = True

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

    @classmethod
    def minimum_node_version(cls) -> Tuple[int, int, int]:
        return (12, 0, 0)

    @classmethod
    def on_settings_read(cls, settings: sublime.Settings) -> bool:
        super().on_settings_read(settings)

        if settings.get("dev_environment") == "sublime_text":
            server_settings = settings.get("settings", {})  # type: Dict[str, Any]

            # add package dependencies into "python.analysis.extraPaths"
            extraPaths = server_settings.get("python.analysis.extraPaths", [])  # type: List[str]
            extraPaths.append("$server_directory_path/_resources/typings")
            extraPaths.extend(cls.find_package_dependency_dirs())
            server_settings["python.analysis.extraPaths"] = extraPaths

            settings.set("settings", server_settings)

        return False

    def on_ready(self, api: ApiWrapperInterface) -> None:
        api.on_notification("telemetry/event", lambda params: self._handle_telemetry(params))

    # -------------- #
    # custom methods #
    # -------------- #

    @staticmethod
    def find_package_dependency_dirs() -> List[str]:
        dep_dirs = sys.path.copy()

        # move the "Packages/" to the last
        # @see https://github.com/sublimelsp/LSP-pyright/pull/26#discussion_r520747708
        packages_path = sublime.packages_path()
        dep_dirs.remove(packages_path)
        dep_dirs.append(packages_path)

        return [path for path in dep_dirs if os.path.isdir(path)]

    def _handle_telemetry(self, params: Dict[str, Any]) -> None:
        event_name = dotted_get(params, "EventName", "")
        measurements = dotted_get(params, "Measurements", {})

        if event_name == "language_server/analysis_complete":
            extras = []  # type: List[str]

            if dotted_get(measurements, "isFirstRun", 0):
                extras.append("first run")

            return self._status_msg(
                "Analysis {file_counts} files completed in {time_s:.3f} seconds. {extra}".format(
                    file_counts="{numFilesAnalyzed}/{numFilesInProgram}".format_map(measurements),
                    time_s=dotted_get(measurements, "elapsedMs", 0) / 1000,
                    extra="({})".format(",".join(extras)) if extras else "",
                )
            )

    @classmethod
    def _plugin_msg(cls, msg: str) -> str:
        return "{}: {}".format(cls.package_name, msg)

    @classmethod
    def _console_msg(cls, msg: str) -> None:
        print(cls._plugin_msg(msg))

    @classmethod
    def _error_msg(cls, msg: str) -> None:
        sublime.error_message(cls._plugin_msg(msg))

    @classmethod
    def _status_msg(cls, msg: str) -> None:
        sublime.status_message(cls._plugin_msg(msg))
