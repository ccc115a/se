// create subprocess
const p = Deno.run({
  cmd: ["callee.bat"],
});

// await its completion
await p.status();
