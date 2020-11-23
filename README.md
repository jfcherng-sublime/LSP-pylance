# LSP-pylance

Python support for Sublime's LSP plugin provided through [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance).

## About Pylance

From Microsoft's statement, Pylance is an enhanced version of [Pyright](https://github.com/microsoft/pyright).
Apart from IntelliCode, which is not working, there are still other improvements.

- Bundled stubs for: `django`, `jmespath`, `matplotlib`, `pandas`, `PIL`, `pygame`
- Bundled native stubs for: `cv2`, `lxml`, `numpy`
- [@faaizajaz](https://github.com/faaizajaz) spoke about some minor differences he found in
  [this comment](https://github.com/jfcherng-sublime/LSP-pylance/issues/2#issuecomment-716548465).
- See [Pylance's changelog](https://marketplace.visualstudio.com/items/ms-python.vscode-pylance/changelog).

## About IntelliCode

Some interesting findings:

- The model file download link: the `output.blob.azureBlobStorage.readSasToken` section in
  https://prod.intellicode.vsengsaas.visualstudio.com/api/v1/model/common/python/intellisense-members-lstm-pylance/output/latest
- Potentially related LSP command:
  `view.run_command('lsp_execute', {"command_name":"python.intellicode.loadLanguageServerExtension", "command_args":{"modelPath":"..."}})`

  But sending that command to Pylance results in a unhandled Promise rejection:

  ```text
  :: --> LSP-pylance workspace/executeCommand(16): {'command': 'python.intellicode.loadLanguageServerExtension', 'arguments': {'modelPath': 'C:\\Users\\XXXXX\\AppData\\Local\\Sublime Text\\Package Storage\\LSP-pylance\\pylance-insiders.vscode-pylance~2020.11.3-pre.1\\_resources\\model\\E61945A9A512ED5E1A3EE3F1A2365B88F8FE_E4E9EADA96734F01970E616FAB2FAC19'}}
  LSP-pylance: (node:16444) UnhandledPromiseRejectionWarning: Error: Debug Failure. False expression.
  LSP-pylance:     at g.<anonymous> (C:\Users\XXXXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\pylance-insiders.vscode-pylance~2020.11.3-pre.1\extension\dist\server.bundle.js:1:76031)
  LSP-pylance:     at Generator.next (<anonymous>)
  LSP-pylance:     at C:\Users\XXXXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\pylance-insiders.vscode-pylance~2020.11.3-pre.1\extension\dist\server.bundle.js:1:72638
  LSP-pylance:     at new Promise (<anonymous>)
  LSP-pylance:     at c (C:\Users\XXXXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\pylance-insiders.vscode-pylance~2020.11.3-pre.1\extension\dist\server.bundle.js:1:72279)
  LSP-pylance:     at g.executeCommand (C:\Users\XXXXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\pylance-insiders.vscode-pylance~2020.11.3-pre.1\extension\dist\server.bundle.js:1:75672)
  LSP-pylance:     at K.executeCommand (C:\Users\XXXXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\pylance-insiders.vscode-pylance~2020.11.3-pre.1\extension\dist\server.bundle.js:1:145631)
  LSP-pylance:     at K.<anonymous> (C:\Users\XXXXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\pylance-insiders.vscode-pylance~2020.11.3-pre.1\extension\dist\pyright.bundle.js:1:581907)
  LSP-pylance:     at Generator.next (<anonymous>)
  LSP-pylance:     at C:\Users\XXXXX\AppData\Local\Sublime Text\Package Storage\LSP-pylance\pylance-insiders.vscode-pylance~2020.11.3-pre.1\extension\dist\pyright.bundle.js:1:569886
  LSP-pylance: (node:16444) UnhandledPromiseRejectionWarning: Unhandled promise rejection. This error originated either by throwing inside of an async function without a catch block, or by rejecting a promise which was not handled with .catch(). To terminate the node process on unhandled promise rejection, use the CLI flag `--unhandled-rejections=strict` (see https://nodejs.org/api/cli.html#cli_unhandled_rejections_mode). (rejection id: 6)
  ```

  I suspect that this is an incompatible node binding issue. `VSCode 1.15.1` uses `Node.js 12.14.1`.
  I try to use `Node.js 12.14.1` on my local machine but in vain, the error is still the same.

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

## How to Dump Variables from VSCode Extension

Take `extension/extension.bundle.js` as an example,

1. Beautify the obfuscated codes. (Online: https://beautifier.io/)
1. At the beginning of the file, add a dedicated output channel:

   ```js
   // create an output channel named "@@ CRACK @@"
   // @see https://code.visualstudio.com/api/references/vscode-api#OutputChannel
   const my_output_panel = require("vscode").window.createOutputChannel("@@ CRACK @@");
   const my_log = (value) => {
     if (typeof value === "object") {
       // otherwise, it may show boring "[Object Object]"
       value = require("util").inspect(value, false, null);
     }

     my_output_panel.appendLine(value);
   };
   ```

1. Dump a variable:

   ```js
   my_log(variable);
   ```

1. If that code is triggered, you should be able to see the variable value in the `@@ CRACK @@` output panel.

## TODO

As of the next ST 3 LSP release,

- `TypeVar` is available. I guess we can always use `typing` from `LSP.plugin.core.typing`.
- Refactor with latest `lsp_utils` features.
