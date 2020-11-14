import json
import sublime

from LSP.plugin.core import sessions
from LSP.plugin.core.typing import Union


VSCODE_SIGNATURES = {
    "clientInfo": {
        "name": "vscode",
        # @see https://github.com/microsoft/vscode/releases/latest
        "version": "1.51.1",
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


def configure_settings_like_vscode(settings: Union[sublime.Settings, dict]) -> None:
    """ Configure the given settings to make it like VSCode's """

    env = VSCODE_SIGNATURES["env"].copy()
    env.update(settings.get("env", {}))  # type: ignore

    if isinstance(settings, sublime.Settings):
        settings.set("env", env)
        return

    if isinstance(settings, dict):
        settings["env"] = env
        return


def use_vscode_client_info() -> None:
    """ Modify the client info of the LSP session to VSCode's """

    # this method will result in all sessions use the modified clientInfo
    # so this should be only executed once...
    if hasattr(sessions, "__use_vscode_client_info"):
        return

    get_initialize_params_original = sessions.get_initialize_params

    def get_initialize_params_modified(*args, **kargs) -> dict:
        params = get_initialize_params_original(*args, **kargs)
        params["clientInfo"].update(VSCODE_SIGNATURES["clientInfo"])
        return params

    sessions.get_initialize_params = get_initialize_params_modified

    setattr(sessions, "__use_vscode_client_info", True)
