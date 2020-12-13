from .server_vs_marketplace_resource import DOWNLOAD_FROM_MARKETPLACE
from .server_vs_marketplace_resource import ServerVsMarketplaceResource
from .typing import SemanticVersion
from .vscode_settings import configure_server_settings_like_vscode
from LSP.plugin import ClientConfig
from LSP.plugin.core.typing import Dict, List, Optional
from lsp_utils import GenericClientHandler
from lsp_utils import ServerResourceInterface

__all__ = ["VsMarketplaceClientHandler"]


class VsMarketplaceClientHandler(GenericClientHandler):
    package_name = ""
    extension_uid = ""
    extension_version = ""
    server_binary_path = ""
    execute_with_node = False
    pretend_vscode = False
    download_from = DOWNLOAD_FROM_MARKETPLACE  # "marketplace" or "pvsc"
    resource_dirs = []  # type: List[str]

    # internal
    __server = None  # type: Optional[ServerVsMarketplaceResource]

    # -------------------------- #
    # VsMarketplaceClientHandler #
    # -------------------------- #

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def minimum_node_version(cls) -> Optional[SemanticVersion]:
        return (12, 14, 1) if cls.execute_with_node else None  # the node version of VSCode 1.15.1

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        variables = super().get_additional_variables()
        variables.update(
            {
                "package_storage": cls.package_storage(),
                "server_directory_path": cls.server_directory_path(),
                "server_path": cls.binary_path(),
            }
        )
        return variables

    @classmethod
    def server_directory_path(cls) -> str:
        return cls.__server.server_directory_path if cls.__server else ""

    # -------------------- #
    # GenericClientHandler #
    # -------------------- #

    @property
    def config(self) -> ClientConfig:
        client_config = super().config

        if self.pretend_vscode:
            configure_server_settings_like_vscode(client_config)

        return client_config

    @classmethod
    def get_command(cls) -> List[str]:
        command = []

        if cls.execute_with_node:
            command.append("node")

        command.append(cls.binary_path())
        command.extend(cls.get_binary_arguments())

        return command

    @classmethod
    def get_binary_arguments(cls) -> List[str]:
        return ["--stdio"] if cls.execute_with_node else []

    @classmethod
    def manages_server(cls) -> bool:
        return True

    @classmethod
    def get_server(cls) -> Optional[ServerResourceInterface]:
        if not cls.__server:
            cls.__server = ServerVsMarketplaceResource.create(
                {
                    "package_name": cls.package_name,
                    "extension_uid": cls.extension_uid,
                    "extension_version": cls.extension_version,
                    "server_binary_path": cls.server_binary_path,
                    "package_storage": cls.package_storage(),
                    "minimum_node_version": cls.minimum_node_version(),
                    "download_from": cls.download_from,
                    "resource_dirs": cls.resource_dirs,
                }
            )
        return cls.__server
