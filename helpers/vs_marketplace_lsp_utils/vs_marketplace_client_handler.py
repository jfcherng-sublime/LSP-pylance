from .client_handler_decorator import HANDLER_MARK_NOTIFICATION, HANDLER_MARK_REQUEST
from .server_vs_marketplace_resource import get_server_vs_marketplace_resource_for_package
from .server_vs_marketplace_resource import ServerVsMarketplaceResource
from .vscode_settings import configure_server_settings_like_vscode
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.settings import read_client_config
from LSP.plugin.core.typing import Any, Dict, List, Optional, Tuple
from lsp_utils.npm_client_handler import ApiWrapper
import inspect
import os
import shutil
import sublime

# Keys to read and their fallbacks.
CLIENT_SETTING_KEYS = {
    "command": [],
    "env": {},
    "experimental_capabilities": {},
    "languages": [],
    "initializationOptions": {},
    "settings": {},
}  # type: ignore


class VsMarketplaceClientHandler(LanguageHandler):
    # To be overridden by subclass.
    package_name = ""
    extension_uid = ""
    extension_version = ""
    server_binary_path = ""
    execute_with_node = False
    pretend_vscode = False
    resource_dirs = []  # type: List[str]

    # Internal
    __server = None  # type: Optional[ServerVsMarketplaceResource]

    def __init__(self):
        super().__init__()
        assert self.package_name
        self.settings_filename = "{}.sublime-settings".format(self.package_name)
        # Calling setup() also here as this might run before `plugin_loaded`.
        # Will be a no-op if already ran.
        # See https://github.com/sublimelsp/LSP/issues/899
        self.setup()

    @classmethod
    def setup(cls) -> None:
        assert cls.package_name
        assert cls.extension_uid
        assert cls.extension_version
        assert cls.server_binary_path
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
            if cls.__server and cls.__server.needs_installation():
                cls.__server.install_or_update(async_io=True)

    @classmethod
    def cleanup(cls) -> None:
        if os.path.isdir(cls.package_storage()):
            shutil.rmtree(cls.package_storage())

    @property
    def name(self) -> str:
        return self.package_name.lower()

    @classmethod
    def minimum_node_version(cls) -> Tuple[int, int, int]:
        return (12, 0, 0)

    @classmethod
    def package_storage(cls) -> str:
        if cls.install_in_cache():
            storage_path = sublime.cache_path()
        else:
            storage_path = os.path.abspath(os.path.join(sublime.cache_path(), "..", "Package Storage"))
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

    @property
    def config(self) -> ClientConfig:
        configuration = {"enabled": self.__server != None}  # type: Dict[str, Any]
        configuration.update(self._read_configuration())

        if not configuration["command"]:
            configuration["command"] = self._default_launch_command()

        self.on_client_configuration_ready(configuration)

        if self.pretend_vscode:
            configure_server_settings_like_vscode(configuration)

        base_settings_path = "Packages/{}/{}".format(self.package_name, self.settings_filename)
        return read_client_config(self.name, configuration, base_settings_path)  # type: ignore

    @classmethod
    def get_binary_arguments(cls):
        """
        Returns a list of extra arguments to append when starting server.
        """
        return ["--stdio"] if cls.execute_with_node else []

    def _read_configuration(self) -> Dict:
        settings = {}  # type: Dict
        loaded_settings = sublime.load_settings(self.settings_filename)
        if loaded_settings:
            changed = self.on_settings_read(loaded_settings)
            if changed:
                sublime.save_settings(self.settings_filename)
            for key, default in CLIENT_SETTING_KEYS.items():
                settings[key] = loaded_settings.get(key, default)
        return settings

    @classmethod
    def on_settings_read(cls, settings: sublime.Settings) -> bool:
        """
        Called when package settings were read. Receives a `sublime.Settings` object.

        Can be used to change user settings, migrating them to new schema, for example.

        Return True if settings were modified to save changes to file.
        """
        return False

    @classmethod
    def on_client_configuration_ready(cls, configuration: Dict) -> None:
        """
        Called with default configuration object that contains merged default and user settings.

        Can be used to alter default configuration before registering it.
        """
        pass

    @classmethod
    def on_start(cls, window) -> bool:
        return cls.__server != None and cls.__server.ready

    def on_initialized(self, client) -> None:
        """
        This method should not be overridden. Use the `on_ready` abstraction.
        """

        api = ApiWrapper(client)
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
