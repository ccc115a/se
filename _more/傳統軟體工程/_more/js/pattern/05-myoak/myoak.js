import { serve } from "https://deno.land/std@0.60.0/http/server.ts";

export const app = {
  middles:[]
}

app.use = function(middle) {
  app.middles.push(middle)
}

app.listen = async function (port) {
  const s = serve({ port })
  for await (const request of s) {
    let ctx = {
      request,
      headers:new Map()
    }
    for (let middle of app.middles) {
      // if (middle(ctx)) break
      middle(ctx)
    }
    if (ctx.body != null) {
      request.respond({
        body:ctx.body,
        headers:ctx.headers
      })
    } else {
      ctx.headers.set('status', 404)
    }
  }
}




