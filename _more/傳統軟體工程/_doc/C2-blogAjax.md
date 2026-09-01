## 案例 2 -- AJAX 網誌
  
我們將前一個 [BlogMVC 《簡易網誌系統》](https://github.com/cccbook/sejs/tree/master/project/blogMvc) 修改成為 Web2.0 作法的 AJAX
系統，新專案網址如下：

* https://github.com/cccbook/sejs/tree/master/project/blogAjax

其原始碼分為前端與後端，前後端之間透過 fetch API 以 JSON 格式進行溝通。

### 後端: Server.js

後端 Server.js 的程式碼如下：

* https://github.com/cccbook/sejs/blob/master/project/blogAjax/server.js

```js
const logger = require('koa-logger')
const router = require('koa-router')()
const koaBody = require('koa-body')
const koaJson = require('koa-json')
const koaStatic = require('koa-static')

const Koa = require('koa')
const app = (module.exports = new Koa())

// "database"

const posts = [] // {id: 0, title: 'aaa', body: 'aaa'}, {id: 1, title: 'bbb', body: 'bbb'}

// middleware

app.use(logger())

// app.use(render)

app.use(koaBody())
app.use(koaStatic('./public'))

// route definitions

router.get('/list', list).get('/post/:id', show).post('/post', create)

app.use(router.routes())
app.use(koaJson())

/**
 * Post listing.
 */

async function list (ctx) {
  // console.log('list: posts=%j', posts)
  ctx.body = posts
}

/**
 * Show post :id.
 */

async function show (ctx) {
  const id = ctx.params.id
  const post = posts[id]
  if (!post) ctx.throw(404, 'invalid post id')
  ctx.body = post
}

/**
 * Create a post.
 */

async function create (ctx) {
  var post = JSON.parse(ctx.request.body)
  const id = posts.push(post) - 1
  console.log('create:id=>', id)
  console.log('create:get=>', post)
  post.created_at = new Date()
  post.id = id
  console.log('create:save=>', post)
  // ctx.redirect('/')
}

// listen
if (!module.parent) {
  app.listen(3000)
  console.log('Server run at http://localhost:3000')
}
```

### 前端: index.html

* https://github.com/cccbook/sejs/blob/master/project/blogAjax/public/index.html

```html
<html>
  <head>
    <title></title>
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
    </section>
    <script src="main.js"></script>
  </body>
</html>
```

### 前端： main.js

前端本身就採用 MVC 架構，程式碼如下：

* https://github.com/cccbook/sejs/blob/master/project/blogAjax/public/main.js

```js
const blog = {
  controller : window,
  view: {},
  model: {}
}

// const R = {}

window.onhashchange = async function () {
  var r
  var tokens = window.location.hash.split('/')
  console.log('tokens=', tokens)
  switch (tokens[0]) {
    case '#show':
      let post = await blog.model.getPost(tokens[1])
      blog.view.show(post)
      break
    case '#new':
      blog.view.new()
      break
    default:
      let posts = await blog.model.list()
      blog.view.list(posts)
      break
  }
}

window.onload = function () {
  window.onhashchange()
}

blog.view.layout = function (title, content) {
  document.querySelector('title').innerText = title
  document.querySelector('#content').innerHTML = content
}

blog.view.list = function (posts) {
  let list = []
  for (let post of posts) {
    list.push(`
    <li>
      <h2>${post.title}</h2>
      <p><a id="show${post.id}" href="#show/${post.id}">Read post</a></p>
    </li>
    `)
  }
  let content = `
  <h1>Posts</h1>
  <p>You have <strong>${posts.length}</strong> posts!</p>
  <p><a id="createPost" href="#new">Create a Post</a></p>
  <ul id="posts">
    ${list.join('\n')}
  </ul>
  `
  return blog.view.layout('Posts', content)
}

blog.view.new = function () {
  return blog.view.layout('New Post', `
  <h1>New Post</h1>
  <p>Create a new post.</p>
  <form>
    <p><input id="title" type="text" placeholder="Title" name="title"></p>
    <p><textarea id="body" placeholder="Contents" name="body"></textarea></p>
    <p><input id="savePost" type="button" onclick="blog.model.savePost()" value="Create"></p>
  </form>
  `)
}

blog.view.show = function (post) {
  return blog.view.layout(post.title, `
    <h1>${post.title}</h1>
    <p>${post.body}</p>
  `)
}

blog.model.savePost = async function () {
  let title = document.querySelector('#title').value
  let body = document.querySelector('#body').value
  let r = await window.fetch('/post', {
    body: JSON.stringify({title: title, body: body}),
    method: 'POST'
  })
  window.location.hash = '#list'
  return r
}

blog.model.getPost = async function (id) {
  let r = await window.fetch('/post/' + id)
  let post = await r.json()
  return post
}

blog.model.list = async function () {
  let r = await window.fetch('/list/')
  let posts = await r.json()
  return posts  
}
```

### 測試程式

由於 Web2.0 以 AJAX 的作法，有很多前端 JavaScript 程式，因此若用 supertest 只能測試到 server.js ，無法測試到前端的 main.js，因此我們得改用 Puppeteer 或 Selenium 這類的《無頭瀏覽器》(headless browser) 進行前端測試，在此我們採用 Puppeteer 示範：

```js
/* eslint-env mocha */
const ok = require('assert').ok
const app = require('./server').listen(3000)
const puppeteer = require('puppeteer')
var browser, page

const opts = {
  // headless: false,
  slowMo: 100,
  timeout: 10000
}

describe('blogAjax', function () {
  before(async function () {
    browser = await puppeteer.launch(opts)
    page = await browser.newPage()
  })
  after(function () {
    browser.close()
    app.close()
  })

  describe('puppeteer', function () {
    it('GET / should see <p>You have <strong>0</strong> posts!</p>', async function () {
      await page.goto('http://localhost:3000', {
        waitUntil: 'domcontentloaded'
      })
      let html = await page.content()
      ok(html.indexOf('<p>You have <strong>0</strong> posts!</p>') >= 0)
    })
    it('click createPost link', async function () {
      await page.click('#createPost')
      let html = await page.content()
      ok(html.indexOf('<h1>New Post</h1>') >= 0)
    })
    it('fill {title:"aaa", body:"aaa"}', async function () {
      await page.focus('#title')
      await page.keyboard.type('aaa')
      await page.focus('#body')
      await page.keyboard.type('aaa')
      await page.click('#savePost')
    })
    it('should see <p>You have <strong>1</strong> posts!</p>', async function () {
      let html = await page.content()
      ok(html.indexOf('<p>You have <strong>1</strong> posts!</p>') >= 0)
    })
    it('should see <p>You have <strong>1</strong> posts!</p>', async function () {
      await page.click('#show0')
      let html = await page.content()
      ok(html.indexOf('<h1>aaa</h1>') >= 0)
    })
  })
})
```

測試結果如下：

```
PS D:\ccc\book\sejs\project\blogAjax> npm run test

> blogajax@0.0.1 test D:\ccc\book\sejs\project\blogAjax
> mocha --timeout 100000

  blogAjax
    puppeteer
  <-- GET /
  --> GET / 200 317ms 1.04kb
  <-- GET /main.js
  --> GET /main.js 200 252ms 2.33kb
  <-- GET /list/
  --> GET /list/ 200 10ms 2b
      √ GET / should see <p>You have <strong>0</strong> posts!</p> (1338ms)
      √ click createPost link (880ms)
  <-- POST /post
create:id=> 0
create:get=> { title: 'aaa', body: 'aaa' }
create:save=> { title: 'aaa',
  body: 'aaa',
  created_at: 2018-11-09T08:18:45.382Z,
  id: 0 }
  --> POST /post 404 133ms -
  <-- GET /list/
  --> GET /list/ 200 5ms 77b
      √ fill {title:"aaa", body:"aaa"} (2849ms)
      √ should see <p>You have <strong>1</strong> posts!</p> (105ms)
  <-- GET /post/0
  --> GET /post/0 200 6ms 75b
      √ should see <p>You have <strong>1</strong> posts!</p> (680ms)


  5 passing (15s)
```

由於 Puppeteer 包含了一整個瀏覽器在裡面，啟動和執行速度都比較慢，因此在測試時會被 mocha 誤認為當機超時，所以必須要加入 --timeout 參數，才不會因測試太久而導致失敗！

所以我們在 package.json 裏的測試指令是： mocha --timeout 100000，完整的 package.json 如下所示：

* https://github.com/cccbook/sejs/blob/master/project/blogAjax/package.json

```json
{
  "name": "blogajax",
  "version": "0.0.1",
  "description": "AJAX 型的網誌",
  "main": "server.js",
  "dependencies": {
    "koa": "^2.5.3",
    "koa-body": "^4.0.4",
    "koa-json": "^2.0.2",
    "koa-logger": "^3.2.0",
    "koa-router": "^7.4.0",
    "koa-static": "^5.0.0"
  },
  "devDependencies": {
    "puppeteer": "^1.9.0"
  },
  "scripts": {
    "test": "mocha --timeout 100000",
    "start": "node server.js"
  },
  "author": "ccc",
  "license": "MIT"
}
```

### 結語

有了 Puppeteer 這樣的測試工具，我們就可以完整的測試前後端的程式碼，而不需總是用人手動花費大量時間去進行測試了！


