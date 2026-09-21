import { Application } from "https://deno.land/x/oak/mod.ts";

export const app = new Application();

app.use((ctx) => {
  ctx.response.body = "Hello World!";
});
