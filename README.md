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

## Disclaimer

This repository is more or less a proof of concept.
The Pylance server code is heavily obfuscated and it's possible that Microsoft has telemetry in it.

- The [license of Pylance](https://marketplace.visualstudio.com/items/ms-python.vscode-pylance/license)
  disallows you to use it in non-Microsoft editors.

  > INSTALLATION AND USE RIGHTS. a) General. You may install and use any number of copies of the
  > software """""only""""" with Microsoft Visual Studio, Visual Studio for Mac, Visual Studio Code,
  > Azure DevOps, Team Foundation Server, and successor Microsoft products and services
  > (collectively, the “Visual Studio Products and Services”) to develop and test your applications...

  See that tiny "only" in the sentence? So if you use this repository, it's on your own risk.

- Microsoft added some codes to Pylance as of `2020.10.3` to prevent itself from being started in
  non-Microsoft editors but LSP-pylance tries to cope with those restrictions and make it working in ST.

## Installation

This package is not published anywhere.

1. Install [LSP](https://packagecontrol.io/packages/LSP) first for sure.
1. Manually clone, which is preferred due to easier update, or download source codes from GitHub to `Packages/LSP-pylance`.
   You **MUST** use `LSP-pylance` as the package/directory name.
1. Restart Sublime Text.
1. Open a `.py` file in a project.
   If there is `LSP-pylance` in the status bar (the bottom-left corner), then it's done right.

## Configuration

There are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-pylance`
- From the command palette `Preferences: LSP-pylance Settings`

## For Developer of This Plugin

### About IntelliCode

<details>

Some interesting findings:

- I am pretty sure that IntelliCode can be run offline.
- Zipped IntelliCode model file download link: the `output.blob.azureBlobStorage.readSasToken` section in
  https://prod.intellicode.vsengsaas.visualstudio.com/api/v1/model/common/python/intellisense-members-lstm-pylance/output/latest
  (not important but just a log: while downloading, VSCode's User-Agent is `vscodeintellicode/1.2.10 vscode/1.51.1`)
- In VSCode, add `"python.trace.server": "verbose"` to `settings.json` to show detailed client/server communications.

  VSCode Intellicode extension sends the following message to Pylance:

  ```text
  [Trace - ...] Sending request 'workspace/executeCommand - (1)'.
  Params: {
      "command": "python.intellicode.loadLanguageServerExtension",
      "arguments": [
          {
              "modelPath": "c:\\Users\\XXXXX\\.vscode\\extensions\\visualstudioexptteam.vscodeintellicode-1.2.10\\cache\\E61945A9A512ED5E1A3EE3F1A2365B88F8FE_E4E9EADA96734F01970E616FAB2FAC19"
          }
      ]
  }
  ```

  I try to do the same thing in ST via:

  ```python
  view.run_command('lsp_execute', {"command_name":"python.intellicode.loadLanguageServerExtension", "command_args":{"modelPath":"..."}})
  ```

  But it results in a unhandled Promise rejection:

  ```text
  :: --> LSP-pylance workspace/executeCommand(8): {'command': 'python.intellicode.loadLanguageServerExtension', 'arguments': {'modelPath': 'C:\\Users\\XXXXX\\Desktop\\E61945A9A512ED5E1A3EE3F1A2365B88F8FE_E4E9EADA96734F01970E616FAB2FAC19'}}
  LSP-pylance: (node:23864) UnhandledPromiseRejectionWarning: Error: Debug Failure. False expression.
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
  LSP-pylance: (Use `node --trace-warnings ...` to show where the warning was created)
  LSP-pylance: (node:23864) UnhandledPromiseRejectionWarning: Unhandled promise rejection. This error originated either by throwing inside of an async function without a catch block, or by rejecting a promise which was not handled with .catch(). To terminate the node process on unhandled promise rejection, use the CLI flag `--unhandled-rejections=strict` (see https://nodejs.org/api/cli.html#cli_unhandled_rejections_mode). (rejection id: 2)
  :: <<< LSP-pylance 8: None
  ```

  I also found that, in VSCode, if you uninstall Intellicode and execute
  `python.intellicode.loadLanguageServerExtension` with `modelPath` via a keybinding like

  ```json
  // C:\Users\XXXXX\AppData\Roaming\Code\User\keybindings.json
  [
    {
      "key": "ctrl+shift+alt+z",
      "command": "python.intellicode.loadLanguageServerExtension",
      "args": {
        "modelPath": "C:\\Users\\XXXXX\\Desktop\\E61945A9A512ED5E1A3EE3F1A2365B88F8FE_E4E9EADA96734F01970E616FAB2FAC19"
      }
    }
  ]
  ```

  then, Pylance will unzip the download model to
  `C:\Users\XXXXX\.vscode\extensions\ms-python.vscode-pylance-2020.11.2\dist\intelliCode`
  and its Intellicode feature gets activated...

To conclude, in VSCode,

- It's not necessary to install VSCode Intellicode to activate Pylance's Intellicode.
  You just need the downloaded zipped model file and properly manually trigger the
  `python.intellicode.loadLanguageServerExtension` command with a keybinding.
- The above procedure works in portable version of VSCode as well.
- The above procedure **WON'T** work in VSCodium even if I copy Python/Pylance to its extension directory.
  But I should probably try again after [this PR](https://github.com/VSCodium/vscodium/pull/568)
  gets included in the next release.
- I guess the secret is in the Python extension or VSCode itself...
- [Someone on Reddit](https://www.reddit.com/r/linux/comments/k0s8qw/vs_code_developers_prevent_running_the_new/gdkxvpe/)
  provides a way to make Pylance run in non-official build of VSCode.
  I am not sure whether it make Intellicode work as well or just make plugin loadable.

  > FYI this seems to fix that error in unofficial builds, you just have to change the following in `product.json`.
  >
  > Add the extension to `extensionAllowedProposedApi`:
  > `"ms-python.python", "ms-python.gather"`
  >
  > Change `nameLong` to:
  >
  > `"Visual Studio Code"`

</details>

### How to Dump Variables in VSCode Extension

<details>

Take `extension/extension.bundle.js` as an example,

1. Beautify the obfuscated codes. (Online: https://beautifier.io/)
1. At the beginning of the file, add a dedicated output channel:

   ```js
   // create an output channel named "@@ CRACK @@"
   // @see https://code.visualstudio.com/api/references/vscode-api#OutputChannel
   const my_output_panel = require("vscode").window.createOutputChannel("@@ CRACK @@");
   const my_log = (...values) => {
     for (let value of values) {
       if (typeof value === "object") {
         // otherwise, it may show boring "[Object Object]"
         value = require("util").inspect(value, false, null);
       }

       my_output_panel.appendLine(value);
     }
   };
   ```

1. Dump a variable:

   ```js
   my_log(variable);
   ```

1. If that code is triggered, you should be able to see the variable value in the `@@ CRACK @@` output panel.

</details>
