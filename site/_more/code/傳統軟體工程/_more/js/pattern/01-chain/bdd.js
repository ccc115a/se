const O = {}

const expect = function (obj) {
  O.obj = obj
  return O
}

O.to = O
O.be = O
O.a = O

O.include = function (child) { return O.obj.indexOf(child) >= 0 }
O.html = function () { return O.obj.indexOf('<html>') >= 0 }

var text = '<html><body>hello!<body></html>'
console.log(expect(text).to.be.a.html())
console.log(expect(text).to.include('hello'))
console.log(expect(text).to.include('world'))
