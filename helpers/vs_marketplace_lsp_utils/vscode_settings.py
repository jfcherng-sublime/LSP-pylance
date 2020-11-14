import json
import sublime

from LSP.plugin.core import sessions
from LSP.plugin.core.typing import Union

__all__ = [
    "configure_lsp_like_vscode",
    "configure_server_settings_like_vscode",
]


# The client info which VSCode sends to a LSP server
VSCODE_CLIENTINFO = {
    "name": "vscode",
    # @see https://github.com/microsoft/vscode/releases/latest
    "version": "1.51.1",
}

# The environment variables used in VSCode
VSCODE_ENV = {
    "ELECTRON_RUN_AS_NODE": "1",
    "VSCODE_NLS_CONFIG": json.dumps(
        {
            "locale": "en-us",
            "availableLanguages": {},
        },
    ),
}


def configure_lsp_like_vscode() -> None:
    """ Modifies the LSP module to make it like VSCode """

    _use_vscode_client_info()


def configure_server_settings_like_vscode(settings: Union[sublime.Settings, dict]) -> None:
    """ Modifies the given settings to make it like VSCode """

    # if the user already has his own setup, we respect it
    env = VSCODE_ENV.copy()
    env.update(settings.get("env", {}))

    if isinstance(settings, sublime.Settings):
        settings.set("env", env)
        return

    if isinstance(settings, dict):
        settings["env"] = env
        return


def _use_vscode_client_info() -> None:
    """ Modifies the client info of the LSP session to make it like VSCode """

    # this method will result in all sessions use the modified clientInfo
    # so this should be only executed once...
    if hasattr(sessions, "__use_vscode_client_info"):
        return

    get_initialize_params_original = sessions.get_initialize_params

    def get_initialize_params_modified(*args, **kwargs) -> dict:
        params = get_initialize_params_original(*args, **kwargs)
        params["clientInfo"].update(VSCODE_CLIENTINFO)
        return params

    sessions.get_initialize_params = get_initialize_params_modified

    setattr(sessions, "__use_vscode_client_info", True)
