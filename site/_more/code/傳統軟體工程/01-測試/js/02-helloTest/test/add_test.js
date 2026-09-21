import { assert } from "https://deno.land/std@0.63.0/testing/asserts.ts";

Deno.test("add test", () => {
  const x = 1 + 2
  assert(x==3)
})
