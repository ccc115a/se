ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ docker run -it --init denoland/deno:1.13.1 repl
Unable to find image 'denoland/deno:1.13.1' locally
1.13.1: Pulling from denoland/deno
38a3d694730c: Pull complete 
73aaf35d5631: Pull complete
1e0484cd2b8f: Pull complete
6d43f0f8f27d: Pull complete
0e44e4f0677f: Pull complete
Digest: sha256:5c5d9732ea8f179c6512f1d45fcf70de97659ec03db0bdba42870b88d8fe11ed
Status: Downloaded newer image for denoland/deno:1.13.1
Deno 1.13.1
exit using ctrl+d or close()
> ls
Uncaught ReferenceError: ls is not defined
    at <anonymous>:2:1
> x=3
Uncaught ReferenceError: x is not defined
    at <anonymous>:2:3
> var x=3
undefined
> var y=5
undefined
> x+y
8
>
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ ls
_more  auto  course  deno  pmedia  riscv2os
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$  docker run -it --init -p 1993:1993 -v $PWD:/app denoland/deno:1.13.1 run --allow-net /app/main.ts
error: Cannot resolve module "file:///app/main.ts".
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ ls
_more  auto  course  deno  pmedia  riscv2os
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ vim
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ ls
_more  auto  course  deno  hello.js  pmedia  riscv2os
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ docker run -it --init -p 1993:1993 -v $PWD:/app denoland/deno:1.13.1 run --allow-net /app/main.ts
error: Cannot resolve module "file:///app/main.ts".
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ docker run -it --init -p 1993:1993 -v $PWD:/app denoland/deno:1.13.1 run --allow-net hello.js
error: Cannot resolve module "file:///hello.js".
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ docker run -it --init -p 1993:1993 -v $PWD:/app denoland/deno:1.13.1 run --allow-net ./hello.js
error: Cannot resolve module "file:///hello.js".
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ docker run -it --init -p 1993:1993 -v denoland/deno:1.13.1 run --allow-net ./hello.js
Unable to find image 'run:latest' locally
docker: Error response from daemon: pull access denied for run, repository does not exist or may require 'docker login': denied: requested access to the resource is denied.
See 'docker run --help'.
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ docker run -it --init -p 1993:1993 -v $PWD:/app denoland/deno:1.13.1 run --allow-net /app/hello.ts
error: Cannot resolve module "file:///app/hello.ts".
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ pwd
/mnt/c/ccc
ccckmit@DESKTOP-O093POU:/mnt/c/ccc$ ls
_more  auto  course  deno  hello.js  pmedia  riscv2os