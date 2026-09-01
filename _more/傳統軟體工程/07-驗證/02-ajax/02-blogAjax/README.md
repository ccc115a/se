# 練習 -- 使用 puppeteer 測試你的 AJAX 程式 (完整)

## deno

手動

1. 請用 deno run -A app.js 執行 ，然後觀看 http://localhost:8000/
2. 使用 deno test 測試
  * deno test -A --unstable deno_test.js
  * 記得第一次
3. 仔細閱讀 deno_test.js 與 app.js
  * 理解其中的程式碼關係！

全自動

1. ./test.sh

## Node.js

若需要更像 node.js 的測試框架可用 https://deno.land/x/test_suite

1. 請用 deno run -A app.js 執行 ，然後觀看 http://localhost:8000/
2. 使用 mocha + puppeteer 測試
  * mocha --timeout 100000
3. 仔細閱讀 test.js 與 app.js
  * 理解其中的程式碼關係！


先執行

```
$ deno run -A app.js
Server run at http://127.0.0.1:8000
``` ㄒ

然後在另一視窗執行

```
$ deno test -A --unstable test.js      
running 1 test from file:///C:/ccc/course/sa/se/08-verify/02-ajax/02-blogAjax/test.js
test Puppteer ... ok (8259ms)

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out (8848ms)        

```