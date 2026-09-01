const assert = require('assert')
const _ = require('../ccclodash')

describe('ccclodash', function () {
  describe('chunk', function () {
    it("_.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]", function () {
      assert.deepStrictEqual(_.chunk(['a', 'b', 'c', 'd'], 2), [
        ['a', 'b'],
        ['c', 'd']
      ])
    })
    it("_.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]", function () {
      assert.deepStrictEqual(_.chunk(['a', 'b', 'c', 'd'], 3), [
        ['a', 'b', 'c'],
        ['d']
      ])
    })
    it("_.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]", function () {
      assert.notDeepStrictEqual(_.chunk(['a', 'b', 'c', 'd'], 3), [
        ['a', 'b'],
        ['c', 'd']
      ])
    })
  })
})
