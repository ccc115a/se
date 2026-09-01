## 練習 -- BDD

講解： 從 lodash 中再度挑選第三個函數，但是這次採用 BDD 的方式。

BDD : Behavior Driven Development  (先寫測試，再寫程式)

1. 挑選第三個 lodash 函數。
2. 選定後用 BDD 的方式寫測試函數，寫好後直接測試，此時會報錯誤。
3. (BDD2) 寫完後再測試，就會回報測試結果 (若成功就沒有錯誤)

範例 

測試 compact_test.ts (已經改為 BDD 語法)

```
PS D:\ccc\ccc109a\se\deno\se\02-test\06-bdd\test> deno test compact_test.ts
Check file:///D:/ccc/ccc109a/se/deno/se/02-test/06-bdd/test/.deno.test.ts
running 1 tests
test compact ... ok (13ms)

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out (234ms)
```

測試 concat_test.ts (尚未實作)

```
PS D:\ccc\ccc109a\se\deno\se\02-test\06-bdd\test> deno test concat_test.ts 
Check file:///D:/ccc/ccc109a/se/deno/se/02-test/06-bdd/test/.deno.test.ts
error: TS2339 [ERROR]: Property 'concat' does not exist on type 'typeof import("file:///D:/ccc/ccc109a/se/deno/se/02-test/06-bdd/src/ccclodash")'.
  expect(_.concat(array, 2, [3], [[4]])).to.equal([1,2,3,[4]])
           ~~~~~~
    at file:///D:/ccc/ccc109a/se/deno/se/02-test/06-bdd/test/concat_test.ts:6:12
```



