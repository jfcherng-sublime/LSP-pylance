import os
import shutil
import sublime
import sublime_lib

from typing import Any, Dict, List, Optional, Tuple

from .my_lsp_utils import ApiWrapper, VscodeMarketplaceClientHandler
from .utils import dotted_get, os_real_abs_join

PACKAGE_NAME = "LSP-pylance"

LSP_PACKAGE_STORAGE_DIR = os_real_abs_join(sublime.cache_path(), "..", "Package Storage")
SERVER_STORAGE_DIR = os_real_abs_join(LSP_PACKAGE_STORAGE_DIR, PACKAGE_NAME)


class LspPylancePlugin(VscodeMarketplaceClientHandler):
    package_name = PACKAGE_NAME
    resource_dirs = ["_resources"]  # type: List[str]

    # @see https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
    extension_uid = "ms-python.vscode-pylance"
    extension_version = "2020.11.0"
    server_binary_path = os.path.join("extension", "dist", "server.bundle.js")
    execute_with_node = True

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
    def setup(cls) -> None:
        super().setup()
        cls.copy_resource_dirs()

    @classmethod
    def copy_resource_dirs(cls) -> None:
        for folder in cls.resource_dirs:
            folder = folder.rstrip("/\\")

            lsp_resource_dir = "{}/{}/".format(SERVER_STORAGE_DIR, folder)
            resource_dir = "Packages/{}/{}/".format(cls.package_name, folder)

            shutil.rmtree(lsp_resource_dir, ignore_errors=True)
            sublime_lib.ResourcePath(resource_dir).copytree(lsp_resource_dir, exist_ok=True)  # type: ignore

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        variables = super().additional_variables() or {}
        variables.update(
            {
                # handy for ST plugin dev
                "lsp_resources_dir": os_real_abs_join(variables["package_cache_path"], "..", "_resources"),
                "sublime_py_files_dir": os.path.dirname(sublime.__file__),
            }
        )

        return variables

    @classmethod
    def minimum_node_version(cls) -> Tuple[int, int, int]:
        return (12, 0, 0)

    def on_ready(self, api: ApiWrapper) -> None:
        api.on_notification("telemetry/event", lambda params: self._handle_telemetry(params))

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
