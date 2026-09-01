import {app} from './app.js'
import { superdeno } from "https://x.nest.land/superdeno@2.3.2/mod.ts";
import { expect } from "https://deno.land/x/expect@v0.2.1/mod.ts";

const bapp = app.handle.bind(app)
Deno.test("/=>Hello World!", async () => {
  await superdeno(bapp).get("/").expect("Hello World!");
  await superdeno(bapp).get("/").expect(200, "Hello World!");
  await superdeno(bapp).get("/").expect("Content-Type", /text/);
  superdeno(bapp).get("/").end((err, res)=>{
    if (err) throw err;
    // const status = res.status
    // console.log('status=', status)
    // expect(res.status).toEqual(201);
  });
/*
  await superdeno(bapp).get("/").expect(200, "Hello World!", (err, res)=>{
    console.log('res.status=', res.status)
    // expect(res.status).toEqual(201);
  });
*/
});
