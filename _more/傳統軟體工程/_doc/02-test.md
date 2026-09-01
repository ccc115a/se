## 第 2 章 -- 測試與 TDD

### 簡介

從實作的觀點看，程式人在學會《程式設計》之後，第一個要學會的軟體工程技能，就是測試。

而學習測試的第一步，就是學習《單元測試》。

等到學會《單元測試》之後，我們才能跨入《整合測試、系統測試、涵蓋度測試、壓力測試》等等進階的測試領域。

現在就讓我們開始透過 node.js 學習《單元測試》這個主題！

### 使用 lodash

我們會從模仿 lodash 專案開始，透過 mocha 套件學習單元測試的方法。

首先，請讀者先看看 lodash 這個專案，這是一個很受歡迎的 JavaScript 函式庫。

* https://lodash.com/docs/

其中有個函數稱為 chunk，是一個用來把陣列分割成小塊的函數。

* https://lodash.com/docs/4.17.10#chunk

大致瞭解這個專案後，請讀者寫個程式來使用該專案，以下是一個使用 chunk 函數的範例。

* https://github.com/cccbook/sejs/blob/master/example/01-test/00-uselodash/main.js

```js
const _ = require('lodash')

console.log("_.chunk(['a', 'b', 'c', 'd'], 2)=", _.chunk(['a', 'b', 'c', 'd'], 2))
// => [['a', 'b'], ['c', 'd']]
 
console.log("_.chunk(['a', 'b', 'c', 'd'], 3)=", _.chunk(['a', 'b', 'c', 'd'], 3))
// => [['a', 'b', 'c'], ['d']]
```

如果我們沒安裝 lodash 就執行該程式，那麼會看到下列錯誤訊息

```
$ node main.js
internal/modules/cjs/loader.js:583
    throw err;
    ^

Error: Cannot find module 'lodash'
    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:581:15)
    at Function.Module._load (internal/modules/cjs/loader.js:507:25)
    at Module.require (internal/modules/cjs/loader.js:637:17)
    at require (internal/modules/cjs/helpers.js:20:18)
    at Object.<anonymous> (D:\course\sejsbook\example\01-test\00-uselodash\main.js:1:73)
    at Module._compile (internal/modules/cjs/loader.js:689:30)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:700:10)
    at Module.load (internal/modules/cjs/loader.js:599:32)
    at tryModuleLoad (internal/modules/cjs/loader.js:538:12)
    at Function.Module._load (internal/modules/cjs/loader.js:530:3)
```

我們可以透過 npm i lodash 這個指令安裝該套件以解決這個問題。

```
$ npm i lodash
+ lodash@4.17.11
added 1 package in 8.364s
```

然後就可以再執行一次該程式。

```
$ node main.js
_.chunk(['a', 'b', 'c', 'd'], 2)= [ [ 'a', 'b' ], [ 'c', 'd' ] ]
_.chunk(['a', 'b', 'c', 'd'], 3)= [ [ 'a', 'b', 'c' ], [ 'd' ] ]
```

現在您應該會使用 lodash 的 chunk 函數了！

但是、這並不是我們這一章的重點，我們的重點是測試。

為了要學習測試，我們必須先撰寫《待測函數》，而 lodash 裡的 chunk 函數，就是我們的第一個模仿對象！

換言之、我們要請讀者模仿 lodash ，並創建一套自己的 lodash，然後再這個模放過程當中，逐漸引入 Node.js 軟體工程的基礎工具，讓大家透過模仿學會《軟體測試》。

就我個人的想法，模仿才是最快的學習方法！

### 模仿 lodash

為了示範這個模仿過程，我建立了下列專案，您可以快速地透過該專案學習到本書前三章的《TDD 測試、NPM 套件、GIT版本管理》等技能。

* https://github.com/cccbook/ccclodash

以下是我所撰寫的 chunk 函數

* https://github.com/cccbook/ccclodash/blob/master/lib/chunk.js

```
function chunk(array = [], n) {
  const clist = [];
  for (let i = 0; i < array.length; i += n) {
    clist.push(array.slice(i, i + n));
  }
  return clist;
}

module.exports = chunk;
```

寫好這樣一個函數之後，一般學生型的作法會是寫個主程式來使用它，像是這樣：

* https://github.com/cccbook/ccclodash/blob/master/example/chunkEx.js

```js
const chunk = require('../lib/chunk')

console.log("chunk(['a', 'b', 'c', 'd'], 2)=", chunk(['a', 'b', 'c', 'd'], 2))
// => [['a', 'b'], ['c', 'd']]

console.log("chunk(['a', 'b', 'c', 'd'], 3)=", chunk(['a', 'b', 'c', 'd'], 3))
// => [['a', 'b', 'c'], ['d']]
```

然後透過執行後檢視的方式，看看結果是否正確：

```
PS D:\course\sejsbook\project\ccclodash\example> node chunkEx.js
chunk(['a', 'b', 'c', 'd'], 2)= [ [ 'a', 'b' ], [ 'c', 'd' ] ]
chunk(['a', 'b', 'c', 'd'], 3)= [ [ 'a', 'b', 'c' ], [ 'd' ] ]
```

如果肉眼檢查輸出結果是正確的，就認為程式是對的，否則就再修改！

但是這樣的方式並不那麼正規，也不容易系統化，因為我們得一個一個去檢查結果是否正確，非常耗費眼力。

在 node.js 裏，較正統的做法是採用 mocha 之類的測試框架進行測試。

以下是我寫的 mocha 測試範例：

```js
const assert = require('assert')
const chunk = require('../lib/chunk')

describe('chunk', function () {
  it("_.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]", function () {
    assert.deepStrictEqual(chunk(['a', 'b', 'c', 'd'], 2), [ [ 'a', 'b' ], [ 'c', 'd' ] ])
  })
  it("_.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]", function () {
    assert.deepStrictEqual(chunk(['a', 'b', 'c', 'd'], 3), [ [ 'a', 'b', 'c' ], [ 'd' ] ])
  })
  it("_.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]", function () {
    assert.notDeepStrictEqual(chunk(['a', 'b', 'c', 'd'], 3), [ [ 'a', 'b' ], ['c', 'd'] ])
  })
})
```

我們可以透過 mocha 套件測試它，以下是我的測試過程。

```
PS D:\course\sejsbook\project\ccclodash> mocha test/chunkTest.js


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]


  3 passing (74ms)
```

要使用 mocha 測試之前，請先用 npm install mocha --global 這樣的指令，將 mocha 安裝在全域的系統資料夾當中，才能直接在命令列裏使用 mocha test/chunkTest.js 這樣的指令進行測試。

如果您還不瞭解 mocha 到底是甚麼，請參考其官網：

* https://mochajs.org/

官網裡面有簡單的範例，您可以試著剪貼後進行測試，通常就會懂了！

```js
var assert = require('assert');
describe('Array', function() {
  describe('#indexOf()', function() {
    it('should return -1 when the value is not present', function() {
      assert.equal([1,2,3].indexOf(4), -1);
    });
  });
});
```

現在、您應該知道單元測試該怎麼做了，輪到你了！

> 進階閱讀： [【單元測試】改變了我程式設計的思維方式](http://www.codedata.com.tw/java/unit-test-the-way-changes-my-programming)


### TDD 測試驅動開發

最近由於《敏捷軟體開發方法》的影響，TDD/BDD 變成一種重要的開發方式，很多專案都會使用 TDD/BDD 的開發方式，問題是：甚麼是 TDD/BDD 呢？

TDD 的全名是 Test Driven Development, BDD 則是 Behavior Driven Development。

但是光看名稱，是無法瞭解 TDD/BDD 之內涵的。

簡單來說， TDD 是一種《測試導向》的系統開發方法，強調《先寫測試、再寫程式》，而不是傳統的《先寫好程式再想測試怎麼寫》！

問題是、先寫測試有甚麼好處呢？

如果你真正開始用 TDD 的方式，先寫測試再寫程式，那麼你就不會用那種《一下就跳入細節》的思考方式，而是先想清楚函數功能，函數的輸入與輸出之規定，長期下來你會發現這種方式蠻有幫助的。

而且當我們先考量測試的時候，通常就會從整個系統的最高層開始想，一層一層的規格寫下來，這樣就有點《由上而下分析定義清楚》的感覺，等到函數規格清楚了，再開始寫程式，所以其實 TDD 會強迫你做系統分析，也不容易寫出一堆根本用不到的程式，而且還會讓你每個函數都確實被測試過，算是一舉數得的做法！

> 進階閱讀 : [搞笑談軟工:關於BDD/TDD的三大誤解](http://teddy-chen-tw.blogspot.com/2014/09/bddtdd.html)

### BDD 行為驅動開發

BDD (Behavior Driven Development) 行為驅動開發，其實可以算是 TDD 的進化版，

TDD 裏的測試，通常採用 assert(...) 之類的敘述，這種語法並不自然，通常只有程式人才會瞭解，一般人看到會很錯愕，因此才會發展出 BDD 這樣的 expect(...) 或 should(...) 語法，採用這種比較容易理解聽懂的語法撰寫測試規格，就稱為 BDD 行為驅動開發。

為了讓同學們進一步體會 BDD，我們將引入另一個套件，那就是 chai ，官方網址如下：

* https://www.chaijs.com/

Chai 套件包含了三種測試寫法，分別是 Should, Expect, Assert ，其中 Assert 屬於 TDD 的語法，而 Should, Expect 則屬於 BDD 的語法。

![Chai 套件的三種測試語法](./img/Chai.png)


Should 語法比 Expect 語法更好寫，但是卻會覆寫修改待測物件，我比較不那麼喜歡，所以在此我們選擇用 Expect 來示範 BDD 語法。

以下是一個使用 BDD 語法的 Chai/Expect 範例，我用來測試自己仿製 lodash 套件的 concat 函數。

* https://github.com/cccbook/ccclodash/blob/master/test/concatTest.js

```js
const expect = require('chai').expect
const concat = require('../lib/concat')

var array = [1]
var other = concat(array, 2, [3], [[4]])

describe('concat', function () {
  it('concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]', function () {
    expect(other).to.deep.equal([1, 2, [3], [[4]]])
    // assert.deepStrictEqual(other, [1, 2, 3, [4]])
  })
  it('concat(array, ....) will not modify array', function () {
    expect(array).to.deep.equal([1])
    // assert.deepStrictEqual(array, [1]);
  })
})
```

上面程式中使用 expect 語法，但是將 assert 語法以註解的行形式寫下，以方便讀者觀察其中的差異！


然後我們再用 mocha 測試之

```
PS D:\course\sejs\project\ccclodash> mocha test/concatTest.js


  concat
    √ concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ concat(array, ....) will not modify array


  2 passing (37ms)
```

對於《中文》使用者而言，很可能感覺不太出來這樣的 BDD 寫法有何特別好處，但是對於《英文》慣用者而言，BDD 寫法就像一般講話那樣，非常的親切易懂。

為了讓讀者更容易體會英文使用者的感受，我們將上述程式改寫成《假想中文版》，如下所示：

```js
const expect = require('chai').expect
const concat = require('../lib/concat')

var array = [1]
var other = concat(array, 2, [3], [[4]])

describe('concat', function () {
  it('concat(array, 2, [3], [[4]]) 完全等於 [1, 2, [3], [[4]]]', function () {
    期望(other).完全.等於([1, 2, [3], [[4]]])
  })
  it('concat(array, ....) 不會修改 array', function () {
    期望(array).完全.等於([1])
  })
})
```

這樣是不是感覺會很親切呢？ 這就是 BDD 的效用，特別是要和《非技術客戶》溝通的時候，會容易很多！

現在您應該能理解 BDD 與 TDD 的差異了，又到了習題時間了，請練習一下 BDD 風格的測試寫法。


> 進階閱讀 : [自動軟體測試、TDD 與 BDD](https://medium.com/@yurenju/%E8%87%AA%E5%8B%95%E8%BB%9F%E9%AB%94%E6%B8%AC%E8%A9%A6-tdd-%E8%88%87-bdd-464519672ac5)

### 結語 

在本章中，我們說明了《單元測試該怎麼作？》，並且進一步學習了《先寫測試、再寫程式》這種 TDD 測試驅動開發的作法，最後又說明了 TDD 的進化版 BDD 這種更自然的測試語法。

就軟體工程的角度，單元測試是一定要作的，不進行測試會讓軟體開發
變得非常危險，隨時都有可能整個系統掛點，或者因錯誤太多而無法繼續開發下去。

TDD 的內涵，除了《先寫測試再寫程式》之外，其實可以用以下三項法則描述：

1. 在編寫好失敗的單元測試之前，不要寫任何產品代碼。
2. 只要有一個單元測試失敗了，就不要再寫測試代碼。無法通過編譯也是一種失敗。
3. 產品代碼恰好能夠讓當前失敗的單元測試成功通過即可，不要多寫。

這樣的做法和《先寫程式再寫測試》的方法相反，比較不會寫出沒用的代碼，而且寫程式的過程也會變得很不一樣，有很清楚的標準可以依循，那就是測試案例 (也就是規格)。

對於是否要採用 TDD，少數人有不同的意見，其中最著名的一篇文章是 David Heinemeier Hansson (DHH) 寫的，連結如下：

* [TDD is dead. Long live testing.](http://david.heinemeierhansson.com/2014/tdd-is-dead-long-live-testing.html), By David Heinemeier Hansson on April 23, 2014

由於 DHH 是著名的 Ruby 套件 Rail 的開發者，因此他的意見特別被重視，但是天才的想法是很難套到一般人的身上的。

我認為 DHH 真正想表達的是，別被 TDD 給綁住了，對於那些規格不那麼清楚，需要自由想像嘗試的時候，別總是拿《先寫測試》作為教條，有時《先寫程式再寫測試》反而會更好，必須視情況而定。

其實到底是先寫程式還是先寫測試，業界朋友也都有很多不同的做法和意見，以下是我在 facebook 上做的一則調查，

* 想請問各位程式人，您的公司是否有採用 TDD/BDD 的做法《先寫測試，再寫程式》呢？
    * https://www.facebook.com/ccckmit/posts/10156531171411893
    * 結果發現，沒有人採用嚴格的 TDD 作法，反而是《同時開發、邊寫邊測》的人比較多！

### 進階閱讀：

1. [如何说服你的同事使用TDD](https://zhuanlan.zhihu.com/p/31662844)
2. [THE PAIN OF DHH](http://my-codeworks.com/blog/the-pain-of-dhh), May 8, 2014 Rant
3. [TDD isn't dead just because DHH can't do it ](https://news.ycombinator.com/item?id=7645852)
4. [TDD is not Dead](https://medium.com/@allanmacgregor/tdd-is-not-dead-180da4e347fe), Allan MacGregor

### 練習 1 -- 使用 mocha/TDD/BDD 進行測試

以下練習請從 lodash 套件中選取三個函數實作，

(請同學將選取的三個函數寫在黑板上，不得與老師及其他同學重複)

> 基本參考：https://github.com/cccbook/sejs/tree/master/example/02-test
> 進階參考: https://github.com/se107a/ccclodash

1. 實作第一個函數並用你的方式進行測試。
    * 參考 ： https://lodash.com/docs/
2. 練習使用 mocha 套件進行測試。
    * 參考 ： https://mochajs.org/
3. 使用 mocha 測試你 01-mylodash 中寫的那個函數。
    * 參考 : [【單元測試】改變了我程式設計的思維方式](http://www.codedata.com.tw/java/unit-test-the-way-changes-my-programming)
4. 採用 TDD 的方式，先寫出第二個函數的測試程式。
    * TDD : 先寫測試，再寫程式 
5. 然後再撰寫第二個函數，並完成測試。
    * 參考 : [搞笑談軟工:關於BDD/TDD的三大誤解](http://teddy-chen-tw.blogspot.com/2014/09/bddtdd.html)
6. 採用 chai/BDD 的方式撰寫第三個函數的測試程式。
    * 參考 : https://www.chaijs.com/guide/styles/#expect
7. 然後再撰寫第三個函數，並完成測試。
    * 參考 : [自動軟體測試、TDD 與 BDD](https://medium.com/@yurenju/%E8%87%AA%E5%8B%95%E8%BB%9F%E9%AB%94%E6%B8%AC%E8%A9%A6-tdd-%E8%88%87-bdd-464519672ac5)
8. 使用 nyc mocha 進行涵蓋度測試。
    * 參考 : https://github.com/istanbuljs/nyc
9. 說明你覺得 TDD/BDD 的優缺點，以及從本次課程學到了甚麼？
    * 參考 : [如何说服你的同事使用TDD](https://zhuanlan.zhihu.com/p/31662844)


做完上述練習，您應該已經學會《單元測試、TDD/BDD》這些技能了，下一章我的重點將會是學習發佈《npm 套件》給別人用的能力！


### 參考文獻

* [Node.js & JavaScript Testing Best Practices](https://medium.com/@me_37286/yoni-goldberg-javascript-nodejs-testing-best-practices-2b98924c9347)
