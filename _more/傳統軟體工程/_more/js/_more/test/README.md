# Test

## Autopilot

```
user@DESKTOP-96FRN6B MINGW64 /d/ccc109/ws/deno/16-se/test (master)
$ deno run -A --unstable pilot1.js 
Check file:///D:/ccc109/ws/deno/16-se/test/pilot1.js
INFO load deno plugin "autopilot_deno" from local "d:\ccc109\ws\deno\16-se\test\.deno_plugins\autopilot_deno_01d30cec9d205cfbaac871ba17c0ba9e.dll"
[2021-01-02 12:11:35] Info: Preparing Autopilot for windows
[2021-01-02 12:11:35] Info: Autopilot setup complete
[2021-01-02 12:11:35] Info: [mod.ts] New AutoPilot instance created
[2021-01-02 12:11:35] Info: [mod.ts] Running type
[2021-01-02 12:11:35] Info: [mod.ts] Running alert
[2021-01-02 12:11:35] Info: [mod.ts] Running screenSize
[2021-01-02 12:11:35] Info: [mod.ts] Running moveMouse
[2021-01-02 12:11:35] Info: [mod.ts] Running screenshot
```


## Puppeteer for deno

* https://github.com/lucacasonato/deno-puppeteer

```
user@DESKTOP-96FRN6B MINGW64 /d/ccc109/ws/deno/16-se/test (master)
$ deno run -A --unstable puppeteer1.js 
Download https://deno.land/x/puppeteer@5.5.1/mod.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/api-docs-entry.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/mod.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/ConsoleMessage.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/PDFOptions.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Errors.js    
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/FrameManager.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/DOMWorld.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Tracing.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/DeviceDescriptors.js     
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Puppeteer.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/BrowserConnector.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/QueryHandler.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/WebWorker.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/FileChooser.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/JSHandle.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Accessibility.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Coverage.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Page.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Target.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Browser.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/EventEmitter.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/ExecutionContext.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Input.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/LifecycleWatcher.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Dialog.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Product.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/EvalTypes.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/HTTPResponse.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/HTTPRequest.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Connection.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/USKeyboardLayout.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/TimeoutSettings.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/SecurityDetails.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/NetworkManager.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/api-docs-entry.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/initialize-deno.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/DeviceDescriptors.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/helper.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/WebWorker.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/assert.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/LifecycleWatcher.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/fetch.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/BrowserWebSocketTransport.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/BrowserConnector.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Dialog.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Coverage.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Errors.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/ConsoleMessage.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/ExecutionContext.d.ts    
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Accessibility.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/std.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/HTTPResponse.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/PDFOptions.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/AriaQueryHandler.js      
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/QueryHandler.d.ts        
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Debug.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Connection.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Puppeteer.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/FileChooser.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/mitt/src/index.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/EventEmitter.d.ts        
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Product.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Tracing.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Target.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/HTTPRequest.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/SecurityDetails.d.ts     
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/TimeoutSettings.d.ts     
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/EvalTypes.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/DOMWorld.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/JSHandle.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Input.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/NetworkManager.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Browser.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/devtools-protocol/types/protocol.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/FrameManager.d.ts        
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/USKeyboardLayout.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/EmulationManager.js      
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Page.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/revisions.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/deno/Puppeteer.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/AriaQueryHandler.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/BrowserWebSocketTransport.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/ConnectionTransport.js
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/PuppeteerViewport.js     
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/helper.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/fetch.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/assert.d.ts
Download https://deno.land/std@0.82.0/bytes/mod.ts
Download https://deno.land/std@0.82.0/fmt/printf.ts
Download https://deno.land/std@0.82.0/io/mod.ts
Download https://deno.land/std@0.82.0/archive/tar.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/mitt/src/index.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/devtools-protocol/types/protocol-mapping.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/Debug.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/EmulationManager.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/revisions.d.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/deno/Launcher.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/deno/BrowserFetcher.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/deno/LaunchOptions.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/PuppeteerViewport.d.ts
Download https://deno.land/std@0.82.0/io/bufio.ts
Download https://deno.land/std@0.82.0/io/readers.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/common/ConnectionTransport.d.ts
Download https://deno.land/std@0.82.0/io/streams.ts
Download https://deno.land/std@0.82.0/io/writers.ts
Download https://deno.land/std@0.82.0/io/ioutil.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/puppeteer/deno/BrowserRunner.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/zip/mod.ts
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/cache.ts
Download https://deno.land/std@0.82.0/encoding/utf8.ts
Download https://deno.land/x/cache@0.2.9/directories.ts
Download https://dev.jspm.io/jszip@3.5.0
Download https://deno.land/x/puppeteer@5.5.1/vendor/puppeteer-core/vendor/zip/types.ts
Download https://deno.land/x/cache@0.2.9/deps.ts
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/support.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/flate.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/zipEntry.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/readable-stream-browser.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/index.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/compressions.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/stream/DataWorker.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/compressedObject.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/base64.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/generate/ZipFileWorker.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/stream/ConvertWorker.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/utils.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/object.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/nodejs/NodejsStreamInputAdapter.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/zipEntries.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/stream/StreamHelper.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/nodejs/NodejsStreamOutputAdapter.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/external.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/reader/StringReader.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/reader/Uint8ArrayReader.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/zipObject.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/crc32.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/defaults.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/reader/ArrayReader.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/utf8.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/stream/DataLengthProbe.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/reader/readerFor.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/reader/NodeBufferReader.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/generate/index.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/nodejsUtils.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/stream/GenericWorker.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/reader/DataReader.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/stream/Crc32Probe.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/load.dew.js
Download https://dev.jspm.io/npm:jszip@3.5.0/lib/signature.dew.js
Download https://deno.land/std@0.80.0/fs/mod.ts
Download https://deno.land/std@0.80.0/path/mod.ts
Download https://deno.land/std@0.80.0/hash/mod.ts
Download https://deno.land/std@0.80.0/hash/hasher.ts
Download https://deno.land/std@0.80.0/hash/_wasm/hash.ts
Download https://deno.land/std@0.80.0/_util/os.ts
Download https://deno.land/std@0.80.0/path/common.ts
Download https://deno.land/std@0.80.0/path/posix.ts
Download https://deno.land/std@0.80.0/path/glob.ts
Download https://deno.land/std@0.80.0/path/win32.ts
Download https://deno.land/std@0.80.0/path/separator.ts
Download https://deno.land/std@0.80.0/path/_interface.ts
Download https://deno.land/std@0.80.0/fs/expand_glob.ts
Download https://deno.land/std@0.80.0/fs/ensure_dir.ts
Download https://deno.land/std@0.80.0/fs/exists.ts
Download https://deno.land/std@0.80.0/fs/move.ts
Download https://deno.land/std@0.80.0/fs/ensure_symlink.ts
Download https://deno.land/std@0.80.0/fs/empty_dir.ts
Download https://deno.land/std@0.80.0/fs/eol.ts
Download https://deno.land/std@0.80.0/fs/ensure_link.ts
Download https://deno.land/std@0.80.0/fs/walk.ts
Download https://deno.land/std@0.80.0/fs/ensure_file.ts
Download https://deno.land/std@0.80.0/fs/copy.ts
Download https://deno.land/std@0.80.0/hash/_wasm/wasm.js
Download https://deno.land/std@0.80.0/encoding/hex.ts
Download https://deno.land/std@0.80.0/encoding/base64.ts
Download https://deno.land/std@0.80.0/path/_util.ts
Download https://deno.land/std@0.80.0/path/_constants.ts
Download https://deno.land/std@0.80.0/fs/_util.ts
Check file:///D:/ccc109/ws/deno/16-se/test/puppeteer1.js
error: Uncaught (in promise) Error: Could not find browser revision 818858. Run "PUPPETEER_PRODUCT=chrome deno run -A --unstable https://deno.land/x/puppeteer@5.5.1/install.ts" to download a supported browser binary.  
      if (missingText) throw new Error(missingText);
                             ^
    at ChromeLauncher.launch (Launcher.ts:94:30)
    at async file:///D:/ccc109/ws/deno/16-se/test/puppeteer1.js:5:17
```