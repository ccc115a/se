import { expect } from 'https://deno.land/x/tdd/mod.ts'
import * as _ from "../src/ccclodash.ts";

Deno.test("concat", () => {
  var array = [1];
  expect(_.concat(array, 2, [3], [[4]])).to.equal([1,2,3,[4]])
})
