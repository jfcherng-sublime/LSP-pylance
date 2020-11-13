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
- The model file download link: https://prod.intellicode.vsengsaas.visualstudio.com/api/v1/model/common/python/intellisense-members/output/latest (Taken from https://github.com/MicrosoftDocs/intellicode/issues/93#issuecomment-490240914)
- Potentially related LSP command: `view.run_command('lsp_execute', {"command_name":"python.intellicode.loadLanguageServerExtension"})`

  But this command results in unhandled Promise rejection:

  ```text
  LSP-pylance: (node:20292) UnhandledPromiseRejectionWarning: Error: Debug Failure. False expression.
  LSP-pylance:     at _0x5f4b25.<anonymous> (C:\Users\XXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\ms-python.vscode-pylance~2020.11.0\extension\dist\server.bundle.js:1500:70)
  LSP-pylance:     at Generator.next (<anonymous>)
  LSP-pylance:     at C:\Users\XXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\ms-python.vscode-pylance~2020.11.0\extension\dist\server.bundle.js:1405:103
  LSP-pylance:     at new Promise (<anonymous>)
  LSP-pylance:     at _0x30cadb (C:\Users\XXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\ms-python.vscode-pylance~2020.11.0\extension\dist\server.bundle.js:1376:28)
  LSP-pylance:     at _0x5f4b25.executeCommand (C:\Users\XXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\ms-python.vscode-pylance~2020.11.0\extension\dist\server.bundle.js:1490:32)
  LSP-pylance:     at _0x5ae44f.executeCommand (C:\Users\XXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\ms-python.vscode-pylance~2020.11.0\extension\dist\server.bundle.js:3000:200)
  LSP-pylance:     at _0x5ae44f.<anonymous> (C:\Users\XXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\ms-python.vscode-pylance~2020.11.0\extension\dist\pyright.bundle.js:17811:46)
  LSP-pylance:     at Generator.next (<anonymous>)
  LSP-pylance:     at C:\Users\XXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\ms-python.vscode-pylance~2020.11.0\extension\dist\pyright.bundle.js:17513:49
  LSP-pylance: (Use `node --trace-warnings ...` to show where the warning was created)
  LSP-pylance: (node:20292) UnhandledPromiseRejectionWarning: Unhandled promise rejection. This error originated either by throwing inside of an async function without a catch block, or by rejecting a promise which was not handled with .catch(). To terminate the node process on unhandled promise rejection, use the CLI flag `--unhandled-rejections=strict` (see https://nodejs.org/api/cli.html#cli_unhandled_rejections_mode). (rejection id: 2)
  ```

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

1. Install [LSP](https://packagecontrol.io/packages/LSP) first for sure.
1. Manually download (or clone) source codes from GitHub to `Packages/LSP-pylance`.
1. Restart Sublime Text.
1. Open a `.py` file in a project.

## Configuration

There are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-pylance`
- From the command palette `Preferences: LSP-pylance Settings`
