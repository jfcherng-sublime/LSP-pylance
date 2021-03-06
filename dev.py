from LSP.plugin.core.typing import Any, Dict, TypeVar
import getpass
import os
import sublime
import sys


T = TypeVar("T")


def expand_variables(val: T) -> T:
    w = sublime.active_window()

    variables = w.extract_variables()
    variables.update(
        {
            "path": (";" if os.name == "nt" else ":").join(sys.path),
            "username": getpass.getuser(),
            "workspaceFolder": (w.folders() or [""])[0],
        }
    )

    return sublime.expand_variables(val, variables)  # type: ignore


def vscode_python_settings() -> Dict[str, Any]:
    settings = {
        "python": {
            "diagnostics": {"sourceMapsEnabled": False},
            "autoComplete": {
                "addBrackets": False,
                "extraPaths": [],
                "showAdvancedMembers": True,
                "typeshedPaths": [],
            },
            "autoUpdateLanguageServer": True,
            "logging": {"level": "info"},
            "experiments": {"enabled": True, "optInto": [], "optOutFrom": []},
            "defaultInterpreterPath": "python",
            "disableInstallationCheck": False,
            "envFile": "${workspaceFolder}/.env",
            "formatting": {
                "autopep8Args": [],
                "autopep8Path": "autopep8",
                "provider": "autopep8",
                "blackArgs": [],
                "blackPath": "black",
                "yapfArgs": [],
                "yapfPath": "yapf",
            },
            "globalModuleInstallation": False,
            "jediMemoryLimit": 0,
            "jediPath": "",
            "languageServer": "Pylance",
            "analysis": {
                "diagnosticPublishDelay": 1000,
                "errors": [],
                "warnings": [],
                "information": [],
                "disabled": [],
                "typeshedPaths": [],
                "cacheFolderPath": "",
                "memory": {"keepLibraryAst": False},
                "logLevel": "Info",
                "symbolsHierarchyDepthLimit": 10,
                "completeFunctionParens": False,
                "autoImportCompletions": True,
                "autoSearchPaths": True,
                "stubPath": "typings",
                "diagnosticMode": "openFilesOnly",
                "extraPaths": [],
                "useLibraryCodeForTypes": True,
                "typeCheckingMode": "off",
                "diagnosticSeverityOverrides": {},
            },
            "linting": {
                "enabled": True,
                "flake8Args": [],
                "flake8CategorySeverity": {"E": "Error", "F": "Error", "W": "Warning"},
                "flake8Enabled": False,
                "flake8Path": "flake8",
                "ignorePatterns": [".vscode/*.py", "**/site-packages/**/*.py"],
                "lintOnSave": True,
                "maxNumberOfProblems": 100,
                "banditArgs": [],
                "banditEnabled": False,
                "banditPath": "bandit",
                "mypyArgs": ["--ignore-missing-imports", "--follow-imports=silent", "--show-column-numbers"],
                "mypyCategorySeverity": {"error": "Error", "note": "Information"},
                "mypyEnabled": False,
                "mypyPath": "mypy",
                "pycodestyleArgs": [],
                "pycodestyleCategorySeverity": {"E": "Error", "W": "Warning"},
                "pycodestyleEnabled": False,
                "pycodestylePath": "pycodestyle",
                "prospectorArgs": [],
                "prospectorEnabled": False,
                "prospectorPath": "prospector",
                "pydocstyleArgs": [],
                "pydocstyleEnabled": False,
                "pydocstylePath": "pydocstyle",
                "pylamaArgs": [],
                "pylamaEnabled": False,
                "pylamaPath": "pylama",
                "pylintArgs": [],
                "pylintCategorySeverity": {
                    "convention": "Information",
                    "error": "Error",
                    "fatal": "Error",
                    "refactor": "Hint",
                    "warning": "Warning",
                },
                "pylintEnabled": True,
                "pylintPath": "pylint",
                "pylintUseMinimalCheckers": True,
            },
            "pythonPath": "python",
            "condaPath": "",
            "pipenvPath": "pipenv",
            "poetryPath": "poetry",
            "sortImports": {"args": [], "path": ""},
            "terminal": {
                "activateEnvironment": True,
                "executeInFileDir": False,
                "launchArgs": [],
                "activateEnvInCurrentTerminal": False,
            },
            "testing": {
                "cwd": None,
                "debugPort": 3000,
                "nosetestArgs": [],
                "nosetestsEnabled": False,
                "nosetestPath": "nosetests",
                "promptToConfigure": True,
                "pytestArgs": [],
                "pytestEnabled": False,
                "pytestPath": "pytest",
                "unittestArgs": ["-v", "-s", ".", "-p", "*test*.py"],
                "unittestEnabled": False,
                "autoTestDiscoverOnSaveEnabled": True,
            },
            "venvFolders": [],
            "venvPath": "",
            "workspaceSymbols": {
                "ctagsPath": "ctags",
                "enabled": False,
                "exclusionPatterns": ["**/site-packages/**"],
                "rebuildOnFileSave": True,
                "rebuildOnStart": True,
                "tagFilePath": "${workspaceFolder}/.vscode/tags",
            },
            "insidersChannel": "off",
            "showStartPage": True,
            "trace": {"server": "verbose"},
        }
    }

    return expand_variables(settings)


def vscode_env() -> Dict[str, str]:
    env = {
        "ALLUSERSPROFILE": "C:\\ProgramData",
        "AMD_ENTRYPOINT": "vs/workbench/services/extensions/node/extensionHostProcess",
        "APPDATA": "C:\\Users\\${username}\\AppData\\Roaming",
        "APPLICATION_INSIGHTS_NO_DIAGNOSTIC_CHANNEL": "true",
        "CHROME_CRASHPAD_PIPE_NAME": "\\\\.\\pipe\\crashpad_2976_RZOBQMWJBTFHPXNM",
        "CommonProgramFiles": "C:\\Program Files\\Common Files",
        "CommonProgramFiles(x86)": "C:\\Program Files (x86)\\Common Files",
        "CommonProgramW6432": "C:\\Program Files\\Common Files",
        "COMPUTERNAME": "${username}-W10-VM",
        "ComSpec": "C:\\Windows\\system32\\cmd.exe",
        "DriverData": "C:\\Windows\\System32\\Drivers\\DriverData",
        "ELECTRON_RUN_AS_NODE": "1",
        "FPS_BROWSER_APP_PROFILE_STRING": "Internet Explorer",
        "FPS_BROWSER_USER_PROFILE_STRING": "Default",
        "HOMEDRIVE": "C:",
        "HOMEPATH": "\\Users\\${username}",
        "LOCALAPPDATA": "C:\\Users\\${username}\\AppData\\Local",
        "LOGONSERVER": "\\\\${username}-W10-VM",
        "NUMBER_OF_PROCESSORS": "8",
        "OneDrive": "C:\\Users\\${username}\\OneDrive",
        "ORIGINAL_XDG_CURRENT_DESKTOP": "undefined",
        "OS": "Windows_NT",
        "Path": "${path}",
        "PATHEXT": ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC",
        "PIPE_LOGGING": "true",
        "PROCESSOR_ARCHITECTURE": "AMD64",
        "PROCESSOR_IDENTIFIER": "Intel64 Family 6 Model 60 Stepping 3, GenuineIntel",
        "PROCESSOR_LEVEL": "6",
        "PROCESSOR_REVISION": "3c03",
        "ProgramData": "C:\\ProgramData",
        "ProgramFiles": "C:\\Program Files",
        "ProgramFiles(x86)": "C:\\Program Files (x86)",
        "ProgramW6432": "C:\\Program Files",
        "PSModulePath": "C:\\Program Files\\WindowsPowerShell\\Modules;C:\\Windows\\system32\\WindowsPowerShell\\v1.0\\Modules",
        "PUBLIC": "C:\\Users\\Public",
        "SESSIONNAME": "Console",
        "SystemDrive": "C:",
        "SystemRoot": "C:\\Windows",
        "TEMP": "C:\\Users\\${username}\\AppData\\Local\\Temp",
        "TMP": "C:\\Users\\${username}\\AppData\\Local\\Temp",
        "USERDOMAIN": "${username}-W10-VM",
        "USERDOMAIN_ROAMINGPROFILE": "${username}-W10-VM",
        "USERNAME": "${username}",
        "USERPROFILE": "C:\\Users\\${username}",
        "VERBOSE_LOGGING": "true",
        "VSCODE_CWD": "C:\\Users\\${username}\\AppData\\Local\\Programs\\Microsoft VS Code",
        "VSCODE_HANDLES_UNCAUGHT_ERRORS": "true",
        "VSCODE_IPC_HOOK": "\\\\.\\pipe\\31d9d0edf1994549ea901159b5c46262-1.51.1-main-sock",
        "VSCODE_IPC_HOOK_EXTHOST": "\\\\.\\pipe\\vscode-ipc-2c4b6893-e896-4bd0-ad37-2ea0c8cc231e-sock",
        "VSCODE_LOG_STACK": "false",
        "VSCODE_LOGS": "C:\\Users\\${username}\\AppData\\Roaming\\Code\\logs\\20201125T142012",
        "VSCODE_NLS_CONFIG": '{{"locale":"en-us","availableLanguages":{{}},"_languagePackSupport":true}}',
        "VSCODE_NODE_CACHED_DATA_DIR": "C:\\Users\\${username}\\AppData\\Roaming\\Code\\CachedData\\e5a624b788d92b8d34d1392e4c4d9789406efe8f",
        "VSCODE_PID": "2976",
        "windir": "C:\\Windows",
    }

    return expand_variables(env)
