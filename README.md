# LSP-pylance

Python support for Sublime's LSP plugin provided through [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance).

## About Pylance

From Microsoft's statement, Pylance is an enhanced version of [Pyright](https://github.com/microsoft/pyright).
Apart from IntelliCode, which won't be available in ST, there are still other improvements.

But actually, I don't know what Pylance has features that are not provided by
[Pyright](https://github.com/microsoft/pyright) in other editors.
[@faaizajaz](https://github.com/faaizajaz) spoke about some minor differences he found in
[this comment](https://github.com/jfcherng-sublime/LSP-pylance/issues/2#issuecomment-716548465).
You can peek [Pylance's changelog](https://marketplace.visualstudio.com/items/ms-python.vscode-pylance/changelog) as well.

## About IntelliCode

Some interesting findings:

- The [vsintellicode.modelDownloadPath](https://github.com/MicrosoftDocs/intellicode/issues/231#issuecomment-708129568) setting in VSCode.

## Disclaimer

This repository is more or less a proof of concept.
The Pylance server code is heavily obfuscated and it's quite possible that Microsoft has telemetry in it.

- The [license of Pylance](https://marketplace.visualstudio.com/items/ms-python.vscode-pylance/license)
  disallows you to use it in non-Microsoft editors.

  > INSTALLATION AND USE RIGHTS. a) General. You may install and use any number of copies of the software """""only""""" with Microsoft Visual Studio, Visual Studio for Mac, Visual Studio Code, Azure DevOps, Team Foundation Server, and successor Microsoft products and services (collectively, the “Visual Studio Products and Services”) to develop and test your applications...

  See that tiny "only" in the sentence? So if you use this repository, it's on your own risk.

- Microsoft added some codes to Pylance as of `2020.10.3` to prevent itself from being started in non-Microsoft editors
  but LSP-pylance tries to crack those restrictions and make it working in ST.

## Installation

This package is not published anywhere.

- Download (or clone) source codes from GitHub.
- Manually install it to `Packages/LSP-pylance`.
- Restart Sublime Text.

## Configuration

There are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-pylance`
- From the command palette `Preferences: LSP-pylance Settings`
