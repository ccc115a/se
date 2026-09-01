# Design (系統設計)

## PDL (Program Description Language)

其實就是演算法，當我們要寫一個程式的時候，先把大架構用《結構化口語》寫下來，
這種結構化口語，就是所謂的《演算法》或者《程式描述語言》 (PDL)。

以下我們以組譯器為例！

## 二階段組譯器

```
Algorithm 組譯器
input 組合語言檔案
output 機器碼檔案
Begin
  第一階段：計算所有符號的位址，建立符號表。
  第二階段：根據指令表與符號表，將組合語言轉換成機器碼。
End

Algorithm 第一階段
input 組合語言檔案
output 符號表
Begin
  開啟組合語言檔
  while (檔案還沒結束)
    讀取一行
    剖析該行
    若該行有符號，則記錄符號位址
    計算下一行位址
  end
End

Algorithm 第二階段
input 組合語言檔案
output 符號表
Begin
  開啟組合語言檔
  while (檔案還沒結束)
    讀取一行
    剖析該行
    將該行《轉為機器碼》
    計算下一行位址
  end
End

Algorithm 剖析
input line; 一行組合語言
output code; 剖析後的結構
Begin
  共有三種情況，分別傳回剖析後結構
    符號行 : (symbol) 
    A 指令 : {@(symbol || number)}
    C 指令 : d = c; j
End

Algorithm 轉為機器碼
input line; 一行組合語言
output code; 機器碼
Begin
  {符號, 類型, 欄位 (d, c, j)} = 剖析(line)
  根據類型進行編碼
    A 型: 數字直接編碼，符號查表後編碼。
    C 型: 查表將 d, c, j 轉為代碼 dx, cx, jx
  code = 0b111<<13|cx<<6|dx<<3|jx
End
```