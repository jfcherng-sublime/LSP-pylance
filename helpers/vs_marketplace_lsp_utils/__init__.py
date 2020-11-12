try:
    from LSP.plugin import __version__ as lsp_version
except ImportError:
    lsp_version = (0, 0, 0)

from lsp_utils.api_wrapper import ApiWrapperInterface

from .server_vs_marketplace_resource import ServerVsMarketplaceResource

if lsp_version >= (1, 0, 0):  # type: ignore
    from .vs_marketplace_client_handler_v2 import VsMarketplaceClientHandler
else:
    from .vs_marketplace_client_handler import VsMarketplaceClientHandler

__all__ = [
    "ApiWrapperInterface",
    "ServerVsMarketplaceResource",
    "VsMarketplaceClientHandler",
]
