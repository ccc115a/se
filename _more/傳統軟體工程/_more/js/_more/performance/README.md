# 效能問題

## 規模化

* [厉害了，淘宝千万并发，14 次架构演进！](https://zhuanlan.zhihu.com/p/341870718)


## 效能

* [為什麼我離開 Medium 用 eleventy 做一個 blog](https://jason-memo.dev/posts/why-i-leave-medium-and-build-blog-with-eleventy/)


打造一個 high performance 的個人 blog 技巧 #

1. 使用靜態頁面
2. self host static asset 盡量 reuse connection 減少 connection 成本
3. inline css in style tag 讓 critical asset 優先下載
4. 盡量使用系統字型，不用額外下載 web font，避免網頁文字跳動跟減少下載資源
5. 使用先進的圖片格式 諸如 webp avif 減少圖片體積大小 ，用 <picture /> tag 設定好 fallback
6. 使用 cdn 服務，cloudflare 免費提供的應該就夠用了，讓世界各地看你的 blog 不會受地理位置影響變慢，還享有 https http/3 的支援服務
7. 用 loading="lazy" html attribute 來 native lazyload image 同時讓 google crawler 可以爬圖片
8. 點擊再載入 codesandbox iframe，讓你的 blog 一開就不需要載入好幾個 vscode 進來

反思 : 

1. [Self-Host Your Static Assets](https://csswizardry.com/2019/05/self-host-your-static-assets/)
2. [SELF HOST STATIC ASSETS](https://www.riklewis.com/2019/08/self-host-static-assets/)

* [Unlimited Scale and Free Web Hosting with GitHub Pages and Cloudflare](https://www.toptal.com/github/unlimited-scale-web-hosting-github-pages-cloudflare)
    * https://stackedit.io/ (Markdown Editor)
    * https://disqus.com/ (討論留言)
    * Customizing the domain name. (echo 'pricecheck.gilani.me' > CNAME)


## HTTP/TLS

* [TLS 1.3 / QUIC 與 HTTP/3 對效能的改善](https://hkt999.medium.com/tls-1-3-quic-%E8%88%87-http-3-%E5%B0%8D%E6%95%88%E8%83%BD%E7%9A%84%E6%94%B9%E5%96%84-a37b2ddcfc95#_=_)

* [HTTP/3 傳輸協議 - QUIC 原理簡介](https://medium.com/@chester.yw.chu/http-3-%E5%82%B3%E8%BC%B8%E5%8D%94%E8%AD%B0-quic-%E7%B0%A1%E4%BB%8B-5f8806d6c8cd)
