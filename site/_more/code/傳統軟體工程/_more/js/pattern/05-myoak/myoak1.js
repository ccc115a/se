function mycall(f, ctx) {
  f(ctx) // hello(myctx)
}

function hello(ctx) {
  console.log(ctx)
  console.log('hello')
}

var myctx = {
  name: 'ccc'
}

mycall(hello, myctx)
// hello(myctx)
