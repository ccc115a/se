/**
 * examples.js — 測試 nn0.js
 * 
 * 執行方法: node examples.js
 */

const { Value, Adam, linear, cross_entropy } = require('../nn0.js');

console.log("=== 測試 Value 基本計算與自動微分 ===");
let a = new Value(2.0);
let b = new Value(3.0);
let c = a.mul(b).add(b.pow(2)); // c = a*b + b^2 = 2*3 + 9 = 15
c.backward();
console.log(`c.data: ${c.data} (預期 15)`);
console.log(`a.grad: ${a.grad} (預期 3，因為 dc/da = b)`);
console.log(`b.grad: ${b.grad} (預期 8，因為 dc/db = a + 2b = 2 + 6 = 8)`);

