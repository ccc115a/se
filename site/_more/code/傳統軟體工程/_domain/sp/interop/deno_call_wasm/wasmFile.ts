const wasmCode = await Deno.readFile("incrementer.wasm");
const wasmModule = new WebAssembly.Module(wasmCode);
const wasmInstance = new WebAssembly.Instance(wasmModule);
const increment = wasmInstance.exports.increment as CallableFunction;
console.log(increment(41));