import {app} from './app.js'

console.log('Server run at http://127.0.0.1:8000')
await app.listen({ hostname: "127.0.0.1", port: 8000 });
