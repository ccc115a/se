import { app } from "./app.js";

console.log('start at : http://127.0.0.1:8000')
await app.listen({ port: 8000 });
