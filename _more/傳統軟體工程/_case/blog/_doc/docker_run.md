# docker run

```
wsl> docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
wsl> docker images
REPOSITORY      TAG       IMAGE ID       CREATED       SIZE
postgres        alpine    b8c450ae0903   3 days ago    192MB
denoland/deno   latest    c6678f922d2c   7 days ago    170MB
gitea/gitea     latest    7737d8e9cae8   9 days ago    148MB
nginx           latest    dd34e67e3371   13 days ago   133MB
mysql           latest    5a4e492065c7   13 days ago   514MB
wsl> docker run -it --name deno_blog denoland/deno /bin/bash
root@d546dff4c50c:/# ls
bin  boot  deno-dir  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var   
root@d546dff4c50c:/# deno
Deno 1.13.2
exit using ctrl+d or close()
> var x=3, y=5;
undefined
> x+y
8
>
root@d546dff4c50c:/# exit
exit
wsl> docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```
