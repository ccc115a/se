# 練習 -- 模仿 lodash 套件實作

## 執行範例

```
PS D:\ccc\ccc109a\se\deno\se\02-test\03-lodashTest> deno run example/ex1.ts
_.chunk(['a', 'b', 'c', 'd'], 2)= [ [ "a", "b" ], [ "c", "d" ] ]
_.chunk(['a', 'b', 'c', 'd'], 3)= [ [ "a", "b", "c" ], [ "d" ] ]
```

## 單元測試

```
csienqu-teacher:test csienqu$ deno test .
Check file:///Users/csienqu/Desktop/ccc/se/deno/se/02-test/03-lodashTest/test/.deno.test.ts
running 1 tests
test chunk ... ok (4ms)

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out (4ms)

```

