# 程式品質 -- 避免 bug

## JavaScript

解決辦法: 認識 pitfall, 採用好的寫法

1. 盡量用 === 取代 ==
2. 加上 lint, 像是 standardJS
3. 別用 object 當字典 (改用 map)
4. 避免使用 with
5. 避免使用 eval
6. 變數前一定要宣告 var, let, const .... (否則會變成全域變數)
7. 運算式盡量用 (...) 標示優先順序
8. 防止 switch 貫穿，要加上 break
9. 加上區塊標示 {...}
10. 使用 new 要很小心，可在建構函數上防護
11. 盡量不要用 for (.. in ...) ，陣列用 for (let i=0; ....)
12. 字串內容是不可修改的
13. 別濫用正規表示法
14. 注意分號插入，所以別任意換行
15. 永不修改 arguments 物件
16. 注意 this 的系結 (箭頭函數是在定義時綁定，但一般 function 是在使用時綁定)
17. 避免繼承基礎類別 (因為那些類別是連結 C 語言的)
18. 小心隱含的強制轉型
19. 別用同步方法呼叫非同步函數 (例如忘記加上 await )




效能增進

1. 避免使用 continue
2. switch 分支多時會很慢，可用查表代替
3. 把最常見的狀況放在 if 的最前面
4. map, forEach 之類的函數比迴圈慢
5. 非必要別用遞迴 (像是費氏數列這類問題用迴圈就好了，即使合併排序也可以寫成迴圈版)
6. 迴圈最佳化 (像是共用運算外提等等 ...)
7. 避免使用 eval
8. 盡量使用原生方法 (querySelector + fetch 取代 jQuery)
9. 動態載入需要的資源 (並且在需要時才載入)
10. 將 <script ...> 寫在網頁最後
11. 避免使用同步的 I/O 函數


## 反例

* [如何写出无法维护的代码](https://coolshell.cn/articles/4758.html)
* [程序员的二八定律](http://www.liriansu.com/pareto-rule-of-programmers)

## 參考

* [軟體缺失導致的危害](https://hackmd.io/@sysprog/software-failure)

