const assert = require('assert')
/**
 * Creates an array of elements split into groups the length of `size`.
 * If `array` can't be split evenly, the final chunk will be the remaining
 * elements.
 * 
 * @memberof _
 * @since 0.1.0
 * @category Array
 * @param {Array} array The array to process.
 * @param {number} [size=1] The length of each chunk
 * @returns {Array} Returns the new array of chunks.
 * @example
 *
 * _.chunk(['a', 'b', 'c', 'd'], 2)
 * // => [['a', 'b'], ['c', 'd']]
 *
 * _.chunk(['a', 'b', 'c', 'd'], 3)
 * // => [['a', 'b', 'c'], ['d']]
 */

function chunk (array = [], n = 1) {
  assert.ok(Number.isInteger(n) && n >= 0, 'chunk: n should be a positive integer')
  assert.ok(Array.isArray(array), 'chunk: first argument should be an array')
  // 如果要做上述檢查，或許可以改用 flow.js 或 typescript, 或用 is.is https://is.js.org/
  const clist = []
  for (let i = 0; i <= array.length; i += n) {
    clist.push(array.slice(i, i + n))
  }
  return clist
}

module.exports = chunk