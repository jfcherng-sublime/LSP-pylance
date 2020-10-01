import sublime


# @see https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
SERVER_VERSION = "2020.9.7"

PLUGIN_NAME = "LSP-pylance"
SETTINGS_FILENAME = "{}.sublime-settings".format(PLUGIN_NAME)

ARCH = sublime.arch()
PLATFORM = sublime.platform()
ST_CHANNEL = sublime.channel()
ST_VERSION = sublime.version()
