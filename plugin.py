import os

from .lsp_utils import VscodeMarketplaceClientHandler


class LspPylancePlugin(VscodeMarketplaceClientHandler):
    package_name = "LSP-pylance"

    # @see https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
    extension_item_name = "ms-python.vscode-pylance"
    extension_version = "2020.10.2"
    server_binary_path = os.path.join("extension", "dist", "server.bundle.js")
    execute_with_node = True
