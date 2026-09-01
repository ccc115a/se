# 練習 e2e 測試 -- 使用 puppeteer

* Puppeteer : Chrome headless browser
* e2e : end to end test

1. 安裝 puppeteer
  * npm i puppeteer
2. 撰寫 puppeteer 測試程式 example.js
  * 參考 [example.js](example.js)
3. 執行 puppeteer 範例
  * node example.js
4. 觀看 [example.png](example.png) 截圖畫面
  * 



## puppeteer

* https://www.aymen-loukil.com/en/blog-en/google-puppeteer-tutorial-with-examples/ (超讚！)
* https://github.com/GoogleChrome/puppeteer
  * 以 chrome 瀏覽器進行 e2e 測試
  * [中文文件](https://zhaoqize.github.io/puppeteer-api-zh_CN/#/?id=puppeteer-%E4%B8%AD%E6%96%87%E6%96%87%E6%A1%A3)
* [2018 iT 邦幫忙鐵人賽: Puppeteer 系列](https://ithelp.ithome.com.tw/users/20103438/ironman/1508)
* https://medium.com/@e_mad_ehsan/getting-started-with-puppeteer-and-chrome-headless-for-web-scrapping-6bf5979dee3e 

## 執行

```
$ PUPPETEER_PRODUCT=chrome deno run -A --unstable https://deno.land/x/puppeteer@9.0.1/install.ts

$ deno run -A --unstable puppeteer1.js

$ deno run -A --unstable ScriptTest.js
Dimensions: { width: 800, height: 600, deviceScaleFactor: 1 }

```

## 參考

類似的 e2e 測試套件還有 nightwatch, selenium 等等。

* Nightwatch : node.js (chrome + firefox)
* Selenium : Java (chrome + firefox)
