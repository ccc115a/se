import _ from "https://dev.jspm.io/lodash";

console.log("_.chunk(['a', 'b', 'c', 'd'], 2)=", _.chunk(['a', 'b', 'c', 'd'], 2))
// => [['a', 'b'], ['c', 'd']]
 
console.log("_.chunk(['a', 'b', 'c', 'd'], 3)=", _.chunk(['a', 'b', 'c', 'd'], 3))
// => [['a', 'b', 'c'], ['d']]
