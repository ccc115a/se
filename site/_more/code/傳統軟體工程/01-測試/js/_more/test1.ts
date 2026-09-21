import { assert } from "https://deno.land/std/testing/asserts.ts";

Deno.test("Test Assert", () => {
  assert(1);
  assert("Hello");
  assert(true);
});