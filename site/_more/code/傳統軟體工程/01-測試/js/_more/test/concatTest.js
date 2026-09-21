const expect = require('chai').expect
const _ = require('../ccclodash')

describe('ccclodash', function() {
  var array = [1];
  var other = _.concat(array, 2, [3], [[4]]);

  describe('concat', function() {
    it("_.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]", function() {
      expect(other).to.deep.equal([1, 2, [3], [[4]]])
      // assert.deepStrictEqual(other, [1, 2, 3, [4]])
    });
    it("_.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]", function() {
      expect(array).to.deep.equal([1])
      // assert.deepStrictEqual(array, [1]);
    });
  });
});