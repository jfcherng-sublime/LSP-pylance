# LSP-pylance

Python support for Sublime's LSP plugin provided through [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance). You may be interested in [LSP-pyright](https://github.com/sublimelsp/LSP-pyright).

## Disclaimer

This repository is more or less a proof of concept.
The [license of Pylance](https://marketplace.visualstudio.com/items/ms-python.vscode-pylance/license)
disallows you to use it in non-Microsoft editors. So if you use this repository, it's on your own risk.

## Installation

1. This plugin is not published on the official Package Control.
   To install, add a custom repository for Package Control with steps described [here](https://github.com/jfcherng-sublime/ST-my-package-control/blob/master/README.md#usage).
1. Install [LSP](https://packagecontrol.io/packages/LSP) and `LSP-pylance` via Package Control.
1. Restart Sublime.

## Configuration

There are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-pylance`
- From the command palette `Preferences: LSP-pylance Settings`
