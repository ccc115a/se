import { app } from './myoak.js'

app.use(function (ctx) {
  ctx.body = `
  <html>
  <head>
  <meta charset="UTF-8">
  </head>
  <body>
    <a href="https://tw.youtube.com">YouTube</a> 訪問
  </body>
  </html>`
})

console.log('server started at http://127.0.0.1:8000')
app.listen(8000)