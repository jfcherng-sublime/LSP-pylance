from LSP.plugin import __version__ as lsp_version

if lsp_version >= (1, 0, 0):  # type: ignore
    # ST 4
    from .vs_marketplace_client_handler_v2 import VsMarketplaceClientHandler
else:
    # ST 3
    from .vs_marketplace_client_handler import VsMarketplaceClientHandler

__all__ = [
    "ApiWrapperInterface",
    "ServerVsMarketplaceResource",
    "VsMarketplaceClientHandler",
]
