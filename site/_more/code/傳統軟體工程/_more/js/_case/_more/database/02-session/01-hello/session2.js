import { Application, Router } from "https://deno.land/x/oak/mod.ts";
import { Session } from "https://deno.land/x/session@1.1.0/mod.ts";

const app = new Application();

// Configuring Session for the Oak framework
const session = new Session({ framework: "oak" });
await session.init();

// Adding the Session middleware. Now every context will include a property
// called session that you can use the get and set functions on
app.use(session.use()(session));

// Creating a Router and using the session
const router = new Router();

router.get("/", async (context) => {
    var pageCount = await context.state.session.get("pageCount")
    pageCount = (pageCount == null) ? 0 : pageCount + 1
    await context.state.session.set("pageCount", pageCount)
    console.log('pageCount=', pageCount)
    context.response.body = `Visited page ${pageCount} times`
});

app.use(router.routes());
app.use(router.allowedMethods());

console.log('server run at http://localhost:8000')
await app.listen({ port: 8000 });
