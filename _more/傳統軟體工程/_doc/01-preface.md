## 第 1 章 -- 軟體工程簡介

### 簡介 -- 為何撰寫本書？

這幾年我在金門大學教《軟體工程》課程的時候，一直有個困擾，那就是找不到《理論與實務兼備的教科書》。

大部分的軟體工程書，為了避免只能和某個程式語言搭配，都會採用《抽象泛論》的方式，這樣才能涵蓋各種平台與領域。

但是《抽離了程式的軟體工程》，又能剩下些甚麼呢？

這樣的軟體工程書籍，對我和學生沒有甚麼幫助！

在使用《與 Github 完全整合的教學法》兩年之後，我終於下定決心，寫一本《軟體工程》的書，以彌補這樣的缺憾。

為了能夠讓《軟體工程》能建築在堅實的程式基礎上，我選擇了和 Node.js 緊密結合，以便讓讀者透過實作學習軟體工程的各方面技能。

雖然這樣可能會讓不熟悉 Node.js 的讀者感到困擾，但是卻能《讓這本軟體工程書變得實用》，或許未來我會再撰寫使用其他語言的軟體工程書也說不定。

在本書的前半部，我們將採用《由下而上》的方式，企圖透過《TDD 測試、NPM 套件、GIT 版本管理、品質與除錯、前後端整合測試》等主題，讓讀者能透過實作打下堅實的基礎，希望這樣的安排能幫助大家《以程式人的角度學習軟體工程》。

接著在本書後半部，我們將採用《由上而下》的方式，透過《專案與團隊、系統分析、系統設計、程式實作、上線營運》等主題，讓讀者能從《宏觀到微觀》、《從系統到代碼》、運用 UML 之類的系統分析方法，幫助大家《從系統分析師的角度學習軟體工程》。

透過這樣《由下而上、再由上而下》的方式，我們希望能讓學習者同時具備《宏觀與微觀》兩種視角，既全面又扎實的感受《軟體工程》，讓軟體工程不再只是《畫畫圖、寫寫報告》的抽象課程，而是對《理論與實戰》都有明顯幫助的課程！

現在、就讓我們從 Node.js 的程式測試開始入手，實際體會軟體工程到底是甚麼吧！

## 習題

練習 1 -- node.js 安裝與使用

> 基本參考：https://github.com/ccccourse/se/tree/master/se/01-preface
> 進階參考: https://ccccourse.github.io/ccclodash/docs/-_.html

1. 請安裝好開發環境，包含 node.js 與 Visual Studio Code
    * https://nodejs.org/en/
    * https://code.visualstudio.com/

2. 請寫一個 node.js 的程式 hello.js 印出 hello
```js
console.log('hello 你好！')
```

3. 請用 node hello.js 執行該程式

```
PS D:\course\sejs\example\01-preface\01-hello> node hello
hello 你好！
```
4. 請查看 lodash 套件
    * https://lodash.com/

5. 請用 npm i lodash 安裝該套件
    * https://github.com/lodash/lodash
```
PS D:\course\sejs\example\01-preface\02-lodash> npm i lodash
npm WARN npm npm does not support Node.js v10.11.0
npm WARN npm You should probably upgrade to a newer version of node as we
npm WARN npm can't make any promises that npm will work with this version.
npm WARN npm Supported releases of Node.js are the latest release of 4, 6, 7, 8, 9.
npm WARN npm You can find the latest version at https://nodejs.org/
+ lodash@4.17.11
updated 1 package in 9.701s
```

6. 請寫一個程式去使用該套件的 chunk 函數 main.js。
```js
const _ = require('lodash')

console.log("_.chunk(['a', 'b', 'c', 'd'], 2)=", _.chunk(['a', 'b', 'c', 'd'], 2))
// => [['a', 'b'], ['c', 'd']]
 
console.log("_.chunk(['a', 'b', 'c', 'd'], 3)", _.chunk(['a', 'b', 'c', 'd'], 3))
// => [['a', 'b', 'c'], ['d']]
```
7. 請用 node main.js 執行你的程式
```
PS D:\course\sejs\example\01-preface\02-lodash> node main.js
_.chunk(['a', 'b', 'c', 'd'], 2)= [ [ 'a', 'b' ], [ 'c', 'd' ] ]
_.chunk(['a', 'b', 'c', 'd'], 3) [ [ 'a', 'b', 'c' ], [ 'd' ] ]
```

做完這個練習，您應該已經會使用 node.js 與基本的 npm 套件安裝使用了，這樣我們就可以進入下一章的《TDD 測試》了。
