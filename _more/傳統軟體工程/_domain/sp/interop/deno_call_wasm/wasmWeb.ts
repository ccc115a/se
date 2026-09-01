const { instance, module } = await WebAssembly.instantiateStreaming(
  fetch("https://wpt.live/wasm/incrementer.wasm"),
);
const increment = instance.exports.increment as (input: number) => number;
console.log(increment(41));