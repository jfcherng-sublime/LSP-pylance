from .client_handler_decorator import notification_handler
from .client_handler_decorator import request_handler
from .vscode_settings import configure_lsp_like_vscode
from .vscode_settings import configure_server_settings_like_vscode
from LSP.plugin import __version__ as lsp_version
from lsp_utils.api_wrapper import ApiWrapperInterface

if lsp_version >= (1, 0, 0):
    # ST 4
    from .vs_marketplace_client_handler_v2 import VsMarketplaceClientHandler
else:
    # ST 3
    from .vs_marketplace_client_handler import VsMarketplaceClientHandler

__all__ = [
    "ApiWrapperInterface",
    "configure_lsp_like_vscode",
    "configure_server_settings_like_vscode",
    "notification_handler",
    "request_handler",
    "ServerVsMarketplaceResource",
    "VsMarketplaceClientHandler",
]
