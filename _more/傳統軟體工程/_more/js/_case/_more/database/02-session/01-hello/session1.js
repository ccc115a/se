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

    // Examples of getting and setting variables on a session
    if (await context.state.session.get("pageCount") === undefined) {
        await context.state.session.set("pageCount", 0);

    } else {
        await context.state.session.set("pageCount", await context.state.session.get("pageCount") + 1);
    }
    
    context.response.body = `Visited page ${await context.state.session.get("pageCount")} times`;
});

app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ port: 8000 });