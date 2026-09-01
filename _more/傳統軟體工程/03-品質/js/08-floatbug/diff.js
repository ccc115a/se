// n 次微分 : 參考 https://en.wikipedia.org/wiki/Finite_difference
function diffn(f, n, x=null, h=0.01) {
  if (n === 0) return f(x)
  h = h/2 // 讓 1, 2, .... n 次微分的最大距離都一樣
  var x1 = (x==null) ? null : x+h
  var x_1 = (x==null) ? null : x-h
  return (diffn(f,n-1,x1) - diffn(f,n-1,x_1))/(2*h)
}

let sin = Math.sin

for (let i=0; i<15; i++) {
  console.log('diffn(sin, %d, PI/3)=%d', i, diffn(sin, i, Math.PI/3))
}

