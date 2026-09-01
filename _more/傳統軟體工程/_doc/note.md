# JavaScript 與軟體工程

JavaScript 語言最大的缺點就是語法太隨便了，而且具有動態語言所具有的一切缺點，像是速度比不上 C/C++/Java/C# ， 語法很分歧且隨興，瀏覽器版本眾多不夠統一等等。

學校教的軟體工程，常常從理論開始探討，講很多原理原則，但卻完全沒有實務操作。

業界的軟體工程，則是著重實務，但理論通常比較少。

我們可以利用實務工具銜接兩者，讓理論能落實到實務上！

當您用過了這些實務工具，再回頭去看理論性的議題，相信必然會有不同的感受才對。

## 限制語法

為了克服語法太隨便的問題，第一步可以用 [use strict](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode) 來限制語法，接著可以用 [JsLint](http://www.jslint.com/) 或 [JsHint](http://jshint.com/) 來禁止寫出那些容易出錯的語法，讓語法嚴格一點。

如果還要更嚴格，那或許可以改用比較像 Ruby/Python 的 [CoffeeScript](http://coffeescript.org/) 或者強型態的 [TypeScript](https://www.typescriptlang.org/) ， 但這樣就不能算是 JavaScript 了！

最近發現一個稱為 [JavaScript Standard Style](http://standardjs.com/readme-zhtw) 的工具，您可以在其 [Demo](http://standardjs.com/demo.html) 工具上測試您的語法是否符合標準，而且很多編輯器 (Sublime, Atom, Visual Studio Code, Vim, Emacs, Brackets, WebStorm) 都有支援檢查語法的 Plugin，這似乎是一個非常好用的《限制語法解決方案》，前提是你要接受 Standard Style 的標準語法就是了。

## 除錯工具

* [Debugging node.js w/node-inspector - YouTube](https://www.youtube.com/watch?v=03qGA-GJXjI)
* [Node.js 系列學習日誌 #26 - 調校 Debug 工具 node-inspector](http://ithelp.ithome.com.tw/question/10161382)
* 重要: 很多工具介紹 -- <http://stackoverflow.com/questions/1911015/how-to-debug-node-js-applications>
* <https://nodejs.org/api/debugger.html>
* <https://github.com/node-inspector/node-inspector>

## 單元測試

我們可以用 node.js 簡單的 assert 進行簡單測試，或者 mocha + chai / Jasmin 這樣的專業框架作 TDD/BDD 單元測試。

* [Node.js 用 mocha 做單元測試並整合 Travis-CI](http://larry850806.github.io/2016/10/02/mocha-travis-ci/) (超讚！)

## 版本管理

使用 Git/Github 是目前最常用的版本管理方式。 當然您也可以用 CVS, SVN 或 Mercurial。

NVM 則可以用來選擇 node 與套件的環境版本！

## 軟體工程

要納入更完整的開發流程，可以考慮採用 GitFlow 或更強大的軟體開發工具。

## 專案管理 

* [使用 Redmine 做專案管理 (PDF)](http://fd.idv.tw/slides/COSCUP/2009/Redmine.pdf)
* [在 Windows 架設 Redmine 專案管理平台的安裝設定筆記](http://blog.miniasp.com/post/2011/12/27/Install-Redmine-on-Windows-Notes.aspx)
* <http://zh.wikipedia.org/wiki/Redmine>
* [Redmine 基本功能介紹](http://blog.longwin.com.tw/2011/03/redmine-intro-function-2011/)

## 系統分析

* http://en.wikipedia.org/wiki/User_story
* [ATDD - User Requirement](http://www.dotblogs.com.tw/hatelove/archive/2013/01/07/learning-tdd-in-30-days-day20-atdd-collecting-user-requirement.aspx)


## 效能分析

* https://github.com/bnoordhuis/node-profiler
* Debugging Performance Issues
 * https://www.joyent.com/developers/node/debug#debugging-performance-issues
* TraceGL -- http://badassjs.com/post/48702496345/tracegl-a-javascript-codeflow-visualization-and

## 整合測試 (Integration Testing)  

* [30天快速上手 TDD Day 8 - Integration Testing & Web UI Testing](https://msdn.microsoft.com/zh-tw/library/dn168871.aspx)

## Web UI test 

* [Integration Testing & Web UI Testing](http://www.dotblogs.com.tw/hatelove/archive/2012/12/10/learning-tdd-in-30-days-day8-integration-testing-and-web-ui-testing-by-selenium-and-webdriver.aspx) -- (使用 Selenium)

## 持續整合 (Continuous integration)

我在 2017 年 3 月 9 日按下列文章的方法，對自己的 <https://github.com/ccckmit/mdo/> 專案進行修改加上 .travis.yml 檔案後提交了測試，一開始失敗了。

* [Node.js 用 mocha 做單元測試並整合 Travis-CI](http://larry850806.github.io/2016/10/02/mocha-travis-ci/)

後來發現原因是我沒有在 package.json 當中加入下列段落，於是修改加入之後，就成功通過測試了。

```json
  "devDependencies": {
     "mocha": "^3.1.0"
  },
```

該次的測試網址為 <https://travis-ci.org/ccckmit/mdo/builds/209273266> 。

相關參考：

* [如何使用Travis CI自動測試?](http://oomusou.io/ci/travis-ci-setup/) (讚！)
* [持續整合 (Continuous integration, CI) 簡介](http://www.dotblogs.com.tw/hatelove/archive/2011/12/25/introducing-continuous-integration.aspx)

```
CI就像鍵盤上的enter鍵這麼自然，在每一次的變更，CI server都幫我們整合所有相關的服務，並將結果回饋給整個團隊，就像隨時隨地都有一個醫生在幫系統作全身健康檢查。
 
檢查項目包括了：
建置source code（也就是Auto Build）
執行測試（各種自動化測試）
執行程式碼分析（包括靜態與動態的程式碼分析）
自動部署（強調單鍵部署、單鍵還原，或是不用按按鍵，且應能區分dev環境、qa環境與prod環境）
資料庫整合（初始化資料、還原資料、更新資料庫Schema等等...）

並用不同的方式，回饋給整個團隊。如：
各種檢查工具產生的分析結果，轉換成圖表、網頁、存入資料庫。
將上述結果通知團隊各個成員，並可觀察趨勢，可與上一次分析結果比較。
將多個專案以透明化且數據化的方式，呈現系統品質，找出專案管理、系統設計、瑕疵追蹤等等重要的趨勢與現象，及早採取改善措施。

核心概念就是一句話：『Build software at every change』。
```

## 上線營運

持續運行: forever/pm2/

IaaS 雲端平台: DigitalOcean / Linode / Amazon EC2
PaaS 雲端平台: Heroku

## 品質管理

* [Refactoring legacy code 簡介](http://www.dotblogs.com.tw/hatelove/archive/2012/12/11/learning-tdd-in-30-days-day9-refactoring-introduction-and-how-to-find-refactoring-target.aspx)
* [Tool:SourceMonitor - 程式碼掃瞄](http://www.dotblogs.com.tw/hatelove/archive/2010/02/10/sourcemonitor.aspx)


## 產品驗收

* [ATDD - ATDD的循環](http://www.dotblogs.com.tw/hatelove/archive/2013/01/08/learning-tdd-in-30-days-day21-atdd-cycle.aspx)

摘要:

```
ATDD 工具
這邊補充一下幾個常見的 ATDD 工具 (筆者比較喜歡表格式的呈現）：
Fit :官網
FitNeese (像 wiki 的 Fit ) : 官網
Selenium : 官網 ，也可以參考前面的修煉文： Integration Testing & Web UI Testing
```

* [BDD - Introduction](http://www.dotblogs.com.tw/hatelove/archive/2013/01/08/learning-tdd-in-30-days-day23-bdd-introduction.aspx)

```
以下是整個開發流程的相關環節，一環扣著一環：
User Story：定義與管理使用者需求
Acceptance Test Cases：定義 user story 的完成事項
BDD 的 Feature 與 Scenario：描述 acceptance test cases 所對應的系統行為
BDD 的 Step Template：用來放 TDD 的測試案例
進入 TDD 循環
```

* [BDD - SpecFlow Introduction](http://www.dotblogs.com.tw/hatelove/archive/2013/01/09/learning-tdd-in-30-days-day24-bdd-specflow-introduction.aspx)

```
SpecFlow
SpecFlow 是一套 open source ，且 under 在 BSD license 。
可直接與 Visual Studio 整合。
專案若需參考到 SpecFlow 的組件，則可以直接透過 NuGet 來下載。
若想了解原始碼，則可以到 Github 上下載。
相關網址：
官網
Visual Studio Gallery: SpecFlow
Document
github
```

## 規模擴充

反向代理

負載平衡

快取加速

平行服務


## 方法：TDD

終於瞭解甚麼是 TDD, ATDD, BDD ....

* <https://msdn.microsoft.com/zh-tw/library/dn387568.aspx>

看完我覺得這些 DD 就是從使用者案例一路落實到 code 的過程，然後其中每一步都要轉化為 code 而且可以測試。
我想這是完成符合規格之專案的方法，但可能不是完成設計優美系統的方法，難怪 DHH 說 I don't TDD.

但這種方法真的很有參考價值！

* 教學文件： [Testing in Node.js](http://code.tutsplus.com/tutorials/testing-in-nodejs--net-35018)

```
 The basic rule is that you can't write any code unless the test runner tells you to.
```

C 語言的 TDD

* http://cpputest.github.io/
* http://www.amazon.com/dp/193435662X/?tag=stackoverfl08-20
* http://stackoverflow.com/questions/2574139/c-programming-and-tdd

## 方法：Scrum 敏捷專案開發

* <http://zh.wikipedia.org/wiki/Scrum>
* [手快一定打手慢，唯快不破的合作方法（上）：Scrum 異于常人的基本假設](http://winston-zh.attlin.com/2015/02/scrum.html)
* [手快一定打手慢，唯快不破的合作方法（中）：Scrum 加速的方式，出招與變招](http://winston-zh.attlin.com/2015/03/scrum.html)
* [手快一定打手慢，唯快不破的合作方法（下）：如何用 Scrum 把妹 ;-)](http://winston-zh.attlin.com/2015/04/scrum.html)


## 參考文獻

* Let’s Code: Test-Driven JavaScript -- <http://www.letscodejavascript.com/>
* Test-Driven JavaScript Development -- <http://tddjs.com/>
 * <ftp://91.193.236.10/pub/docs/linux-support/programming/JavaScript/[Pearson]%20-%20Test-Driven%20JavaScript%20Development%20-%20[Johansen].pdf>

* <http://stackoverflow.com/questions/300855/javascript-unit-test-tools-for-tdd>
 * <http://karma-runner.github.io/0.12/index.html>
 * <http://angular.github.io/protractor/>
 * <https://github.com/jquery/testswarm/>
* <http://mochajs.org/>
 * [Testing in Node.js](http://code.tutsplus.com/tutorials/testing-in-nodejs--net-35018), 讚!
 * [Asynchronous, Test-Driven Development, with JavaScript and Mocha](http://www.codemag.com/Article/1308061)
 * [The Difference Between TDD and BDD](https://joshldavis.com/2013/05/27/difference-between-tdd-and-bdd/)
* <http://jasmine.github.io/> -- Behavior-Driven JavaScript
 * <http://jasmine.github.io/edge/introduction.html>
 * <https://github.com/jasmine/jasmine>

```
Karma is a JavaScript test-runner built with Node.js, and meant for unit testing.

Protractor is for end-to-end testing, and uses Selenium Web Driver to drive tests.
```

* <http://mochajs.org/> -- JavaScript test framework for node.js and the browser
* <http://chaijs.com/> --  BDD / TDD assertion library for node and the browser 
* [30天快速上手TDD](http://www.dotblogs.com.tw/hatelove/category/6685.aspx),讚! (30 篇!)
* [關於BDD/TDD的三大誤解](http://teddy-chen-tw.blogspot.tw/2014/09/bddtdd.html)
 * 和傳統的方式不同之處在於，TDD的規格本身就是可執行文件（請參考〈BDD（1）：詳盡的文件就是可用的軟體〉），將規格以可執行的「測試案例」來表達。
* BDD vs TDD (explained)
 * <https://youtu.be/mT8QDNNhExg>
* 30天快速上手 TDD Day 23 - BDD - Introduction 
 * <https://msdn.microsoft.com/zh-tw/library/dn308251.aspx>
* [TDD 已死，測試萬歲](http://blog.littlelin.info/posts/2014/04/26/tdd-is-dead-long-live-testing)
* [RoR之父批TDD已死，你認同嗎？](http://www.ithome.com.tw/news/87245)
* [返璞歸真 -- 以最適當的方式設計軟體](http://blog.xdite.net/posts/2014/04/28/back-to-basic)
