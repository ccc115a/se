import { assertEquals, assertThrows } from "https://deno.land/std@0.63.0/testing/asserts.ts";
import * as _ from "../chunk.ts";

Deno.test("chunk", () => {
  assertEquals(_.chunk(['a', 'b', 'c', 'd'], 2), [['a','b'], ['c','d']])
  assertEquals(_.chunk(['a', 'b', 'c', 'd'], 3), [['a','b', 'c'], ['d']])
  /*
  assertThrows(() => {
    _.chunk({a:1, b:2, c:3, d:4 }, 2)
  })
  */
  assertThrows(() => {
    _.chunk(['a', 'b', 'c', 'd'], -1)
  })
})
