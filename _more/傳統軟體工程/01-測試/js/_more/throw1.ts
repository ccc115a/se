import { assertThrows } from "https://deno.land/std/testing/asserts.ts";

// 以下有 throw，所以都通過 assertThrows 的要求
Deno.test("doesThrow", function (): void {
  assertThrows((): void => {
    throw new TypeError("hello world!");
  });
  assertThrows((): void => {
    throw new TypeError("hello world!");
  }, TypeError);
  assertThrows(
    (): void => {
      throw new TypeError("hello world!");
    },
    TypeError,
    "hello",
  );
});

// 以下沒有 throw，所以反而不通過 assertThrows 的要求
// This test will not pass
Deno.test("fails", function (): void {
  assertThrows((): void => {
    console.log("Hello world");
  });
});
