import { assertEquals } from "https://deno.land/std@0.63.0/testing/asserts.ts";
import * as _ from "../src/ccclodash.ts";

Deno.test("compact", () => {
  assertEquals(_.compact([0, 1, false, 2, '', 3]), [ 1, 2, 3])
})
