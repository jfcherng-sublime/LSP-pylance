from .client_handler_decorator import notification_handler
from .client_handler_decorator import request_handler
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
    "ServerVsMarketplaceResource",
    "VsMarketplaceClientHandler",
    # decorator-related
    "notification_handler",
    "request_handler",
]
