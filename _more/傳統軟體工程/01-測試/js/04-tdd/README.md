## 練習 -- TDD

講解： 從 lodash 中再度挑選第二個函數，但是這次採用 TDD 的方式。

TDD : Test Driven Development  (先寫測試，再寫程式)

1. 挑選第二個 lodash 函數。
2. 選定後寫測試函數，寫好後直接測試，此時會報錯誤。

範例

```
S D:\ccc\ccc109a\se\deno\se\02-test\04-tdd> deno test ./test/chunk_test.ts
running 1 tests
test chunk ... ok (43ms)

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out (173ms)

PS D:\ccc\ccc109a\se\deno\se\02-test\04-tdd> deno test ./test/compact_test.ts
Check file:///D:/ccc/ccc109a/se/deno/se/02-test/04-tdd/.deno.test.ts
error: TS2339 [ERROR]: Property 'compact' does not exist on type 'typeof import("file:///D:/ccc/ccc109a/se/deno/se/02-test/04-tdd/src/ccclodash")'.
  assertEquals(_.compact([0, 1, false, 2, '', 3]), [ 1, 2, 3])
                 ~~~~~~~
    at file:///D:/ccc/ccc109a/se/deno/se/02-test/04-tdd/test/compact_test.ts:5:18

```
