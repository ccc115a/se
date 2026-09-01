# 練習 -- 除錯 (debug)

1. 找出 chunk.js 程式中的 bug


## 討論

我們是否應該對每個參數的型態範圍做嚴格檢查呢？ 

* https://www.facebook.com/ccckmit/posts/10156495068846893
* https://www.reddit.com/r/javascript/comments/2arcwr/should_we_be_validating_function_arguments/
* https://www.joyent.com/node-js/production/design/errors
    * 這篇認為我們應該嚴格檢查並立即報錯 (丟出例外, callback error 或用 EventEmitter emit error)
    * 只要和《API文件》中的規格不一樣，就立刻報錯！

所以作者建議這樣寫

```js
/*
 * Make a TCP connection to the given IPv4 address.  Arguments:
 *
 *    ip4addr        a string representing a valid IPv4 address
 *
 *    tcpPort        a positive integer representing a valid TCP port
 *
 *    timeout        a positive integer denoting the number of milliseconds
 *                   to wait for a response from the remote server before
 *                   considering the connection to have failed.
 *
 *    callback       invoked when the connection succeeds or fails.  Upon
 *                   success, callback is invoked as callback(null, socket),
 *                   where `socket` is a Node net.Socket object.  Upon failure,
 *                   callback is invoked as callback(err) instead.
 *
 * This function may fail for several reasons:
 *
 *    SystemError    For "connection refused" and "host unreachable" and other
 *                   errors returned by the connect(2) system call.  For these
 *                   errors, err.errno will be set to the actual errno symbolic
 *                   name.
 *
 *    TimeoutError   Emitted if "timeout" milliseconds elapse without
 *                   successfully completing the connection.
 *
 * All errors will have the conventional "remoteIp" and "remotePort" properties.
 * After any error, any socket that was created will be closed.
 */
function connect(ip4addr, tcpPort, timeout, callback) {
  assert.equal(typeof (ip4addr), 'string',
      "argument 'ip4addr' must be a string");
  assert.ok(net.isIPv4(ip4addr),
      "argument 'ip4addr' must be a valid IPv4 address");
  assert.equal(typeof (tcpPort), 'number',
      "argument 'tcpPort' must be a number");
  assert.ok(!isNaN(tcpPort) && tcpPort > 0 && tcpPort < 65536,
      "argument 'tcpPort' must be a positive integer between 1 and 65535");
  assert.equal(typeof (timeout), 'number',
      "argument 'timeout' must be a number");
  assert.ok(!isNaN(timeout) && timeout > 0,
      "argument 'timeout' must be a positive integer");
  assert.equal(typeof (callback), 'function');

  /* do work */
}
```

但是我看到的大部分 node.js 程式碼，通常不會使用這種預防錯誤的 assert 。

例如你可以看到 lodash 的 chunk 並沒有處理 array 參數不是陣列的狀況

* https://github.com/lodash/lodash/blob/master/chunk.js

我想是因為若參數不是陣列，最後結果還是會錯誤，在測試時自然無法通過！

(但用 assert 可以提早讓這個錯誤被報出來！可是每個函數都要加實在太麻煩。)

如果對這類防護的要求很高，或許應該考慮改用 TypeScript

* http://www.typescriptlang.org/
    * https://en.wikipedia.org/wiki/TypeScript


