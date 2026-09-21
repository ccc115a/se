
let a = Number.MAX_VALUE // Math.PI*1e80
let b = Number.MIN_VALUE // Math.E/1e80
let c = Math.PI

console.log('a=', a)
console.log('b=', b)
console.log('c=', c)
console.log('a+b=', a+b)
console.log('b+a=', b+a)
console.log('a+b+c=', a+b+c)
console.log('2*a=', 2*a)
console.log('a+a=', a+a)
console.log('a*2=', a*2)
console.log('b/2=', b/2)
console.log('(b*2)/2=', (b*2)/2)
console.log('(a*2)/2=', (a*2)/2)
console.log('1/3=', 1/3)
console.log('0.1+0.2=', 0.1+0.2)

if ((a+b)===(b+a)) {
  console.log('a+b === b+a')
} else {
  console.log('a+b !== b+a')
}

if ((a+b)+c===a+(b+c)) {
  console.log('(a+b)+c === a+(b+c)')
} else {
  console.log('(a+b)+c !== a+(b+c)')
}

console.log('0.1+0.2===0.3', 0.1+0.2===0.3)
