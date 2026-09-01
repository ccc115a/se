// --allow-run
const p = Deno.run({
  cmd: ["python", "callee.py"], 
  stdout: "piped",
  stderr: "piped"
});

console.log('deno: caller run!')
const output = await p.output() // "piped" must be set
const outStr = new TextDecoder().decode(output);

const error = await p.stderrOutput();
const errorStr = new TextDecoder().decode(error);

p.close(); // Don't forget to close it

console.log(outStr, errorStr);