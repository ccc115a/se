import { assert } from "https://deno.land/std@0.63.0/testing/asserts.ts";

export function chunk (array = [], n) {
  assert(typeof n === 'number' && n > 0 && Number.isInteger(n))
  assert(Array.isArray(array))
  const clist = []
  for (let i = 0; i < array.length; i += n) {
    clist.push(array.slice(i, i + n))
  }
  return clist
}

