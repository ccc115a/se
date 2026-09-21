import { assert } from "https://deno.land/std@0.63.0/testing/asserts.ts";

Deno.test("Array", () => {
  assert([1,2,3].indexOf(4) === -1);
  assert([1,2,3].indexOf(3) === 2);
})
