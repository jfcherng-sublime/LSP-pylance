try:
    from LSP.plugin import __version__ as lsp_version
except ImportError:
    lsp_version = (0, 0, 0)

from .server_vscode_marketplace_resource import ServerVscodeMarketplaceResource

if lsp_version >= (1, 0, 0):
    from .vscode_marketplace_client_handler_v2 import VscodeMarketplaceClientHandler
else:
    from .vscode_marketplace_client_handler import VscodeMarketplaceClientHandler

__all__ = [
    "VscodeMarketplaceClientHandler",
    "ServerVscodeMarketplaceResource",
]
