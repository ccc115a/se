# wsl

```
$ wsl
wsl> deno run -A app.js
Server run at http://127.0.0.1:8000
list:posts= [
  { id: 1, title: "aaa", body: "aaaaa" },
  { id: 2, title: "bbb", body: "bbb" },  
  { id: 3, title: "ccc", body: "cccc" }, 
  { id: 4, title: "ddd", body: "ddddd" } 
]
create:post= { title: "eee", body: "eeeee" }
list:posts= [
  { id: 1, title: "aaa", body: "aaaaa" },
  { id: 2, title: "bbb", body: "bbb" },
  { id: 3, title: "ccc", body: "cccc" },
  { id: 4, title: "ddd", body: "ddddd" },
  { id: 5, title: "eee", body: "eeeee" }
]
```