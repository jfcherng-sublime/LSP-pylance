import sublime
import json
import os

from LSP.plugin.core.typing import Any, Dict, List, Optional, Tuple

from .my_lsp_utils import ApiWrapper, VscodeMarketplaceClientHandler
from .utils import dotted_get


class LspPylancePlugin(VscodeMarketplaceClientHandler):
    package_name = "LSP-pylance"

    # @see https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
    extension_item_name = "ms-python.vscode-pylance"
    extension_version = "2020.10.3"
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
    def on_client_configuration_ready(cls, configuration: Dict[str, Any]) -> None:
        # add necessary env variables in order to use Pylance as of 2020.10.3
        configuration["env"].update(
            {
                "ELECTRON_RUN_AS_NODE": "1",
                "VSCODE_NLS_CONFIG": json.dumps(
                    {
                        "locale": "en-us",
                        "availableLanguages": {},
                    }
                ),
            }
        )

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        variables = super().additional_variables() or {}
        variables.update(
            {
                # handy for ST plugin dev to include "sublime.py" and "sublime_plugin.py"
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
