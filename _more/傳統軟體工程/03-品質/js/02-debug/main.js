import {chunk} from './chunk.js'

console.log("chunk(['a', 'b', 'c', 'd'], 2)=", chunk(['a', 'b', 'c', 'd'], 2))
console.log("chunk(['a', 'b', 'c', 'd'], 3)=", chunk(['a', 'b', 'c', 'd'], 3))
console.log("chunk(abcd, 2)=", chunk('abcd', 2))
console.log("chunk({a,b,c,d}, 2)=", chunk({a:1,b:2,c:3,d:4}, 2))
console.log("chunk(['a', 'b', 'c', 'd'], -1)=", chunk(['a', 'b', 'c', 'd'], -1))
