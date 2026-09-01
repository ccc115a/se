# 自動排版

# deno fmt



## 檢查

```
wsl> deno fmt --check add.js

from /mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/course/sa/js/quality/01-format/add.js:
1 | -
2 | -
3 | -function add(a,b) {
1 | +function add(a, b) {
4 | -  return a             + b
5 | -    }
2 | +  return a + b;
3 | +}

```

## 直接格式化

```
wsl> deno fmt add2.js
/mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/course/sa/js/quality/01-format/add2.js
Checked 1 file
```

## 隨堂練習 -- 自動排版

單檔

```
PS D:\ccc\ccc109a\se\deno\se\05-quality\01-format> deno fmt chunk_ugly.js
\\?\D:\ccc\ccc109a\se\deno\se\05-quality\01-format\chunk_ugly.js
```

整個資料夾

```
PS D:\ccc\ccc109a\se\deno\se\05-quality\01-format> deno fmt
D:\ccc\ccc109a\se\deno\se\05-quality\01-format\chunk_ugly.js
D:\ccc\ccc109a\se\deno\se\05-quality\01-format\compact.js
```

## 反例: 不可讀的代碼

* [國際C語言混亂程式碼大賽](https://zh.wikipedia.org/wiki/%E5%9B%BD%E9%99%85C%E8%AF%AD%E8%A8%80%E6%B7%B7%E4%B9%B1%E4%BB%A3%E7%A0%81%E5%A4%A7%E8%B5%9B)
  * http://blog.jobbole.com/93692/ (讚！)
  * http://www0.us.ioccc.org/years.html
  * http://nuccacafe.blogspot.com/2009/04/c-international-obfuscated-c-code.html


