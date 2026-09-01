const assert = require('assert')
const _ = require('../ccclodash')

describe('ccclodash', function() {
  describe('compact', function() {
    it("_.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]", function() {
      assert.deepStrictEqual(_.compact([0, 1, false, 2, '', 3]), [ 1, 2, 3])
    });
  });
});