# debug

請為 chunk.js 除錯！

```
PS D:\ccc\ccc109a\se\deno\se\05-quality\02-debug> deno run main.js
chunk(['a', 'b', 'c', 'd'], 2)= [ [ "a", "b" ], [ "c", "d" ], [] ]
chunk(['a', 'b', 'c', 'd'], 3)= [ [ "a", "b", "c" ], [ "d" ] ]
chunk(abcd, 2)= [ "ab", "cd", "" ]
chunk({a,b,c,d}, 2)= []
// 然後當掉 ....
```
