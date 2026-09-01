function hello(ctx) {
  console.log('ctx=', ctx)
  console.log('hello')
}

var f = hello
var myctx = {path:'/aaa/bbb.html'}

f(myctx) // hello(myctx)
