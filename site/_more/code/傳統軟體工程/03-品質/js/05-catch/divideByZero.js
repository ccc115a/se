

function f1(a, b, c) {
  // if (!Number.isFinite(a/b)) throw Error('f1: a/b is infinity...')
  return (a / b) + c
}

var x = f1(10, 0, 2)
console.log('x = ', x)

