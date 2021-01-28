import os

# For checking the latest version of Pylance:
#     - https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
#     - https://pvsc.blob.core.windows.net/pylance-insiders?restype=container&comp=list

EXTENSION_UID = "pylance-insiders.vscode-pylance"
EXTENSION_VERSION = "2021.1.4-pre.1"
SERVER_BINARY_PATH = os.path.join("extension", "dist", "server.bundle.js")
