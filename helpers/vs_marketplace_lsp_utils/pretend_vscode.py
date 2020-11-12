import json

from LSP.plugin.core import sessions
from LSP.plugin.core.typing import Any, Dict

from . import VsMarketplaceClientHandler

vscode_signatures = {
    "clientInfo": {
        "name": "vscode",
        "version": "1.50.1",
    },
    "env": {
        "ELECTRON_RUN_AS_NODE": "1",
        "VSCODE_NLS_CONFIG": json.dumps(
            {
                "locale": "en-us",
                "availableLanguages": {},
            },
        ),
    },
}


##### BEGIN: override server env #####


@classmethod
def on_client_configuration_ready(cls, configuration: Dict[str, Any]) -> None:
    configuration["env"].update(vscode_signatures["env"])


VsMarketplaceClientHandler.on_client_configuration_ready = on_client_configuration_ready  # type: ignore

##### END: override server env #####


##### BEGIN: override LSP.plugin.core.sessions.get_initialize_params #####

get_initialize_params_original = sessions.get_initialize_params


def get_initialize_params_modified(*args, **kargs) -> dict:
    params = get_initialize_params_original(*args, **kargs)
    params["clientInfo"].update(vscode_signatures["clientInfo"])
    return params


sessions.get_initialize_params = get_initialize_params_modified

##### END: override LSP.plugin.core.sessions.get_initialize_params #####
