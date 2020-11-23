import os

# example download URL for version quick test
# https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
# https://pvsc.blob.core.windows.net/pylance-insiders/vscode-pylance-2020.11.3-pre.1.vsix

EXTENSION_UID = "pylance-insiders.vscode-pylance"
EXTENSION_VERSION = "2020.11.3-pre.1"
SERVER_BINARY_PATH = os.path.join("extension", "dist", "server.bundle.js")
