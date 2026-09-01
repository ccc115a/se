// myoak
let app = {}

let flist = []

var myctx = {
  url: '/aaa/bbb'
}

app.use = function(f) {
   flist.push(f)
}

app.run = function () {
  for (let f of flist) {
    f(myctx)
  }
}

function hello(ctx) {
  ctx.isHello = true
  console.log('hello!')
}

// server example
app.use(hello)

app.use(function (ctx) {
  console.log('ctx=', ctx)
  console.log('world!')
})

app.run()
console.log('flist=', flist)


