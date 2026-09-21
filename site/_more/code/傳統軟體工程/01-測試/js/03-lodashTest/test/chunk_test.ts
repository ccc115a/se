import { assertEquals, assertThrows } from "https://deno.land/std@0.63.0/testing/asserts.ts";
import * as _ from "../src/ccclodash.ts";

Deno.test("chunk", () => {
  assertEquals(_.chunk(['a', 'b', 'c', 'd'], 2), [['a','b'], ['c','d']])
  assertEquals(_.chunk(['a', 'b', 'c', 'd'], 3), [['a','b', 'c'], ['d']])
  assertThrows((): void => {
    _.chunk(['a', 'b', 'c', 'd'], 0)
  })
  // assertEquals(_.chunk(['a', 'b', 'c', 'd'], 3), [['a','b'], ['c','d']])
})
