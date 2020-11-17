from .client_handler_decorator import HANDLER_MARK_NOTIFICATION, HANDLER_MARK_REQUEST
from .server_vs_marketplace_resource import get_server_vs_marketplace_resource_for_package
from .server_vs_marketplace_resource import ServerVsMarketplaceResource
from .vscode_settings import configure_server_settings_like_vscode
from LSP.plugin import AbstractPlugin
from LSP.plugin import ClientConfig
from LSP.plugin import register_plugin
from LSP.plugin import Session
from LSP.plugin import unregister_plugin
from LSP.plugin import WorkspaceFolder
from LSP.plugin.core.types import ResolvedStartupConfig
from LSP.plugin.core.typing import Any, Dict, List, Optional, Tuple
from lsp_utils.npm_client_handler_v2 import ApiWrapper
import inspect
import os
import shutil
import sublime
import weakref

# Keys to read and their fallbacks.
CLIENT_SETTING_KEYS = {
    "command": [],
    "env": {},
    "experimental_capabilities": {},
    "languages": [],
    "initializationOptions": {},
    "settings": {},
}  # type: ignore


class VsMarketplaceClientHandler(AbstractPlugin):
    package_name = ""
    extension_uid = ""
    extension_version = ""
    server_binary_path = ""
    execute_with_node = False
    pretend_vscode = False
    resource_dirs = []  # type: List[str]

    # Internal
    __server = None  # type: Optional[ServerVsMarketplaceResource]

    @classmethod
    def setup(cls) -> None:
        register_plugin(cls)
        if not cls.package_name:
            print("ERROR: [lsp_utils] package_name is required to instantiate an instance of {}".format(cls))

    @classmethod
    def cleanup(cls) -> None:
        unregister_plugin(cls)
        if os.path.isdir(cls.package_storage()):
            shutil.rmtree(cls.package_storage())

    @classmethod
    def name(cls) -> str:
        return cls.package_name

    @classmethod
    def minimum_node_version(cls) -> Tuple[int, int, int]:
        return (12, 0, 0)

    @classmethod
    def package_storage(cls) -> str:
        if cls.install_in_cache():
            storage_path = sublime.cache_path()
        else:
            storage_path = cls.storage_path()
        return os.path.join(storage_path, cls.package_name)

    @classmethod
    def binary_path(cls) -> str:
        return cls.__server.binary_path if cls.__server else ""

    @classmethod
    def server_directory_path(cls) -> str:
        return cls.__server.server_directory if cls.__server else ""

    @classmethod
    def install_in_cache(cls) -> bool:
        return False

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        return {
            "package_storage": cls.package_storage(),
            "server_directory_path": cls.server_directory_path(),
            "server_path": cls.binary_path(),
        }

    @classmethod
    def configuration(cls) -> Tuple[sublime.Settings, str]:
        name = cls.name()
        basename = "{}.sublime-settings".format(name)
        filepath = "Packages/{}/{}".format(name, basename)
        settings = sublime.load_settings(basename)
        settings.set("enabled", True)
        languages = settings.get("languages", None)
        if languages:
            settings.set("languages", cls._upgrade_languages_list(languages))
        cls.on_settings_read(settings)

        # Read into a dict so we can call old API "on_client_configuration_ready" and then
        # resave potentially changed values.
        settings_dict = {}
        for key, default in CLIENT_SETTING_KEYS.items():
            settings_dict[key] = settings.get(key, default)

        cls.on_client_configuration_ready(settings_dict)
        for key in CLIENT_SETTING_KEYS.keys():
            settings.set(key, settings_dict[key])

        return settings, filepath

    @classmethod
    def _upgrade_languages_list(cls, languages):
        upgraded_list = []
        for language in languages:
            if "document_selector" in language:
                language.pop("scopes", None)
                language.pop("syntaxes", None)
                upgraded_list.append(language)
            elif "scopes" in language:
                upgraded_list.append(
                    {
                        "languageId": language.get("languageId"),
                        "document_selector": " | ".join(language.get("scopes")),
                    }
                )
            else:
                upgraded_list.append(language)
        return upgraded_list

    @classmethod
    def on_pre_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List[WorkspaceFolder],
        resolved: ResolvedStartupConfig,
    ) -> Optional[str]:
        if cls.pretend_vscode:
            configure_server_settings_like_vscode(resolved)

            if not resolved.command:
                resolved.command = cls._default_launch_command()

    @classmethod
    def get_binary_arguments(cls) -> List[str]:
        """
        Returns a list of extra arguments to append when starting server.
        """
        return ["--stdio"] if cls.execute_with_node else []

    @classmethod
    def on_settings_read(cls, settings: sublime.Settings) -> bool:
        """
        Called when package settings were read. Receives a `sublime.Settings` object.

        Can be used to change user settings, migrating them to new schema, for example.

        Return True if settings were modified to save changes to file.
        """
        return False

    @classmethod
    def on_client_configuration_ready(cls, configuration: Dict[str, Any]) -> None:
        """
        Called with default configuration object that contains merged default and user settings.

        Can be used to alter default configuration before registering it.
        """
        pass

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        if not cls.__server:
            cls.__server = get_server_vs_marketplace_resource_for_package(
                cls.package_name,
                cls.extension_uid,
                cls.extension_version,
                cls.server_binary_path,
                cls.package_storage(),
                cls.minimum_node_version(),
                cls.resource_dirs,
            )
            if cls.__server:
                return cls.__server.needs_installation()
        return False

    @classmethod
    def install_or_update(cls) -> None:
        cls.__server.install_or_update(async_io=False)

    @classmethod
    def can_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List[WorkspaceFolder],
        configuration: ClientConfig,
    ) -> Optional[str]:
        if not cls.__server or cls.__server.error_on_install:
            return "{}: Error installing server dependencies.".format(cls.package_name)
        if not cls.__server.ready:
            return "{}: Server installation in progress...".format(cls.package_name)
        return None

    def __init__(self, weaksession: "weakref.ref[Session]") -> None:
        super().__init__(weaksession)
        if not self.package_name:
            return

        api = ApiWrapper(self)
        self._register_custom_server_event_handlers(api)
        self.on_ready(api)

    def on_ready(self, api: ApiWrapper) -> None:
        pass

    # -------------- #
    # custom methods #
    # -------------- #

    def _register_custom_server_event_handlers(self, api: ApiWrapper) -> None:
        for _, func in inspect.getmembers(self, predicate=inspect.isroutine):
            event_names = getattr(func, HANDLER_MARK_NOTIFICATION, [])  # type: List[str]
            for event_name in event_names:
                api.on_notification(event_name, func)

            event_names = getattr(func, HANDLER_MARK_REQUEST, [])  # type: List[str]
            for event_name in event_names:
                api.on_request(event_name, func)

    @classmethod
    def _default_launch_command(cls) -> List[str]:
        command = []  # type: List[str]

        if cls.execute_with_node:
            command.append("node")

        command.append(cls.binary_path())
        command.extend(cls.get_binary_arguments())

        return command
