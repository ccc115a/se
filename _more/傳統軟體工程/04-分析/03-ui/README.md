# 介面分析設計

搭配 usecase 與 sequence diagram，設計 iPos 的重要畫面

## 懶人設計法

可以偷就偷，註冊畫面差不多像這樣！

![iPos 註冊畫面](../img/signup.png)

登入畫面

![iPos 登入畫面](../img/signin.png)

## POS 訂購畫面

直接用 markdown 設計


品項選單▼    附加選單▼    數量選單▼  小計_

品名 | 單價 | 附加   | 加價 | 數量 | 小計
-----|-----|-------|------|------|--------
綠茶 | 20  | 加鮮奶 | 10   |  3   | 90
珍珠奶茶 | 35  |    |      |  1   | 30

    總價: 120    【送出】  【放棄】


1. 本介面使用 markdown 設計
  * 符號: ▼ 代表選單, _ 代表輸入欄位, 【...】
 代表按鈕
  * 也可以加上 html 語法直接設計，只是在 github 上無法很好的呈現該設計。
  * 例如 :按鈕 <button>送出</button> 選擇框 <select><option>綠茶</option><option>紅茶</option></select>
2. 或者也可以使用 plantuml 設計 -- http://plantuml.com/salt 
3. 也可以用 ppt 或 slide 設計
4. 當然也可以用更專業的工具，像是 AxureRP 或 Visual Studio ...

## 今日報表


訂單摘要 | 價格 | 狀態 | 結帳者 | 訂購時間
--------|------|------|--------|-------
綠茶 3 .| 120  | 已結帳 | 小雅  | 3:45
紅茶 3 .| 60   | 未結帳 |       | 3:47
.....   | .... | .... |  ...   | ....


## 參考

* [如何设计出易用的 UX — 对话式设计](http://blog.xdite.net/posts/2018/10/07/design-by-conversation)
