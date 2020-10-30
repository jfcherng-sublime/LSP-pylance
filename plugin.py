import json
import os
import sublime

from LSP.plugin.core.typing import Any, Dict, Optional, Tuple

from .lsp_utils import VscodeMarketplaceClientHandler


class LspPylancePlugin(VscodeMarketplaceClientHandler):
    package_name = "LSP-pylance"

    # @see https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
    extension_item_name = "ms-python.vscode-pylance"
    extension_version = "2020.10.3"
    server_binary_path = os.path.join("extension", "dist", "server.bundle.js")
    execute_with_node = True

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
