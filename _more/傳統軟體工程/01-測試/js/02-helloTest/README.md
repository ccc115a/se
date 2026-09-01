# 學習使用 deno test 進行測試

## 測試單檔

```
PS D:\ccc\ccc109a\se\deno\se\02-test\02-helloTest\test> deno test add_test.js
Check file:///D:/ccc/ccc109a/se/deno/se/02-test/02-helloTest/test/.deno.test.ts
running 1 tests
test add test ... ok (11ms)

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out (143ms)
```

## 測試全部

```
PS D:\ccc\ccc109a\se\deno\se\02-test\02-helloTest\test> deno test .
Check file:///D:/ccc/ccc109a/se/deno/se/02-test/02-helloTest/test/.deno.test.ts
running 2 tests
test add test ... ok (18ms)
test Array ... ok (1ms)

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out (22ms)
```
