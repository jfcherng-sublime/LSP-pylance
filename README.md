# LSP-pylance

Python support for Sublime's LSP plugin provided through [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance). You may be interested in [LSP-pyright](https://github.com/sublimelsp/LSP-pyright).

Actually, I don't know what `Pylance` has features that are not provided by
[Pyright](https://github.com/microsoft/pyright) in other editors.
[@faaizajaz](https://github.com/faaizajaz) spoke about some minor differences he found in
[this](https://github.com/jfcherng-sublime/LSP-pylance/issues/2#issuecomment-716548465) comment.

## Disclaimer

This repository is more or less a proof of concept.
The [license of Pylance](https://marketplace.visualstudio.com/items/ms-python.vscode-pylance/license)
disallows you to use it in non-Microsoft editors.

> INSTALLATION AND USE RIGHTS. a) General. You may install and use any number of copies of the software """"""""""""""""""""only"""""""""""""""""""" with Microsoft Visual Studio, Visual Studio for Mac, Visual Studio Code, Azure DevOps, Team Foundation Server, and successor Microsoft products and services (collectively, the “Visual Studio Products and Services”) to develop and test your applications. b) Third Party Components. The software may include third party components with separate legal notices or governed by other agreements, as may be described in the ThirdPartyNotices file(s) accompanying the software.

See that tiny "only" in the sentence? So if you use this repository, it's on your own risk.
Microsoft may have telemetry so they will know if people are using it from other editors.

## Installation

This package is not published anywhere.

- Download (or clone) source codes from GitHub.
- Manually install it to `Packages/LSP-pylance`.
- Restart Sublime Text.

## Configuration

There are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-pylance`
- From the command palette `Preferences: LSP-pylance Settings`
