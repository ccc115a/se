## 第 9 章 -- 實作

### 經典網誌系統 BlogMVC 

在本章我們將主要以一個經典的網誌系統 BlogMVC 為例，說明程式實作階段的進行方式。您可以在下列網址看到 BlogMVC 專案完整的程式碼：

* https://github.com/cccbook/sejs/tree/master/project/blogMvc


### MVC 模式

BlogMVC 專案採用 MVC (Model-View-Controller) 模式，

* Model : model.js
    * 資料的存取
* View : view.js
    * 畫面的顯示
* Controller : Server.js
    * 伺服器主程式，採用 koa ，負責調用 model 與 view 

### Server 主程式

伺服器 Server.js 的原始碼如下：

* https://github.com/cccbook/sejs/tree/master/project/blogMvc/server.js

```js
const V = require('./view')
const M = require('./model')
const logger = require('koa-logger')
const router = require('koa-router')()
const koaBody = require('koa-body')

const Koa = require('koa')
const server = module.exports = new Koa()

server.use(logger())
server.use(koaBody())

router.get('/', list)
  .get('/post/new', add)
  .get('/post/:id', show)
  .post('/post', create)

server.use(router.routes())

async function list (ctx) {
  const posts = M.list()
  ctx.body = await V.list(posts)
}

async function add (ctx) {
  ctx.body = await V.new()
}

async function show (ctx) {
  const id = ctx.params.id
  const post = M.get(id)
  if (!post) ctx.throw(404, 'invalid post id')
  ctx.body = await V.show(post)
}

async function create (ctx) {
  const post = ctx.request.body
  M.add(post)
  ctx.redirect('/')
}

if (!module.parent) {
  server.listen(3000)
  console.log('Server run at http://localhost:3000')
}

```

而負責資料存取的 model 模組之原始碼如下：

```js
const M = module.exports = {}

const posts = []

M.add = function (post) {
  const id = posts.push(post) - 1
  post.created_at = new Date()
  post.id = id
}

M.get = function (id) {
  return posts[id]
}

M.list = function () {
  return posts
}

```

負責呈現畫面的 view 模組之原始碼如下：

```js
var V = module.exports = {}

V.layout = function (title, content) {
  return `
  <html>
  <head>
    <title>${title}</title>
    <style>
      body {
        padding: 80px;
        font: 16px Helvetica, Arial;
      }
  
      h1 {
        font-size: 2em;
      }
  
      h2 {
        font-size: 1.2em;
      }
  
      #posts {
        margin: 0;
        padding: 0;
      }
  
      #posts li {
        margin: 40px 0;
        padding: 0;
        padding-bottom: 20px;
        border-bottom: 1px solid #eee;
        list-style: none;
      }
  
      #posts li:last-child {
        border-bottom: none;
      }
  
      textarea {
        width: 500px;
        height: 300px;
      }
  
      input[type=text],
      textarea {
        border: 1px solid #eee;
        border-top-color: #ddd;
        border-left-color: #ddd;
        border-radius: 2px;
        padding: 15px;
        font-size: .8em;
      }
  
      input[type=text] {
        width: 500px;
      }
    </style>
  </head>
  <body>
    <section id="content">
      ${content}
    </section>
  </body>
  </html>
  `
}

V.list = function (posts) {
  let list = []
  for (let post of posts) {
    list.push(`
    <li>
      <h2>${post.title}</h2>
      <p><a href="/post/${post.id}">讀取貼文</a></p>
    </li>
    `)
  }
  let content = `
  <h1>貼文列表</h1>
  <p>您總共有 <strong>${posts.length}</strong> 則貼文!</p>
  <p><a href="/post/new">創建新貼文</a></p>
  <ul id="posts">
    ${list.join('\n')}
  </ul>
  `
  return V.layout('貼文列表', content)
}

V.new = function () {
  return V.layout('新增貼文', `
  <h1>新增貼文</h1>
  <p>創建一則新貼文</p>
  <form action="/post" method="post">
    <p><input type="text" placeholder="Title" name="title"></p>
    <p><textarea placeholder="Contents" name="body"></textarea></p>
    <p><input type="submit" value="Create"></p>
  </form>
  `)
}

V.show = function (post) {
  return V.layout(post.title, `
    <h1>${post.title}</h1>
    <p>${post.body}</p>
  `)
}

```


### 練習 1 -- AJAX 專案的建立與測試

1. 請學會使用 puppeteer
    * https://github.com/GoogleChrome/puppeteer
2. 請閱讀 helloAjax 的原始碼並執行之
    * https://github.com/cccnqu/se107a/tree/master/example/06-browser/01-puppeteer
3. 請用 mocha + puppeteer 測試 helloAjax
    * mocha test.js
4. 請閱讀 blogAjax 的原始碼並執行之
    * https://github.com/cccnqu/se107a/tree/master/example/06-browser/03-blogAjax
5. 請用 mocha + puppeteer 測試 blogAjax
    * mocha test.js

附加

1. 請學會使用 browserify
    * https://github.com/cccnqu/se107a/tree/master/example/06-browser/10-browserify
2. 請學會使用 babel
    * https://github.com/cccnqu/se107a/tree/master/example/06-browser/12-es6/
<!--
5. 請學會使用 rollup
    * https://github.com/cccnqu/se107a/tree/master/example/06-browser/12-es6/03-rollup/
2. 請學會使用 gulp
    * https://github.com/cccnqu/se107a/tree/master/example/06-browser/11-gulp
3. 請學會使用 webpack
    * https://github.com/cccnqu/se107a/tree/master/example/06-browser/12-webpack
-->


### 練習 3 -- iChat 程式設計

1. 請用 TDD/BDD 的方式，先寫出測試案例！
2. 分配函數模組給成員，撰寫程式碼
3. 反覆上述過程，直到第一版完成。(可以修正設計)

