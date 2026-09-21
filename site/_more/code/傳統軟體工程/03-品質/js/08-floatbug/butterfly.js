// 參考: https://en.wikipedia.org/wiki/Butterfly_effect
function f(x) {
  return 4.0*x*(1.0-x)
}

var a=0.8, b=0.800000000001
for (let i=0; i<100; i++) {
  a = f(a)
  b = f(b)
  console.log(i, ':a=', a, 'b=', b)
}
