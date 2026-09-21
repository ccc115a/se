import { expect } from 'https://deno.land/x/tdd/mod.ts'
import * as _ from "../src/ccclodash.ts";

Deno.test("concat", () => {
  var array = [1];
  var c1 = _.concat(array, 2, [3], [[4]])
  expect(c1).to.equal([1,2,3,[4]])
})
