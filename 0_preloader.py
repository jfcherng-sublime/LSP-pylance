# ------------------------------------------------------------------------------------------------ #
# This file will be loaded before "plugin.py" because Package Control loads modules in dict order. #
# ------------------------------------------------------------------------------------------------ #

from LSP.plugin.core import sessions

##### BEGIN: override LSP.plugin.core.sessions.get_initialize_params #####

get_initialize_params_original = sessions.get_initialize_params


def get_initialize_params_modified(*args, **kwargs) -> dict:
    params = get_initialize_params_original(*args, **kwargs)
    params.update(
        {
            # meow, I am VSCode
            "clientInfo": {
                "name": "vscode",
                "version": "1.50.1",
            },
        }
    )

    return params


sessions.get_initialize_params = get_initialize_params_modified

##### END: override LSP.plugin.core.sessions.get_initialize_params #####
