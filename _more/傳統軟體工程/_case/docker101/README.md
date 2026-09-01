# docker101

## 來源

* https://github.com/dockersamples/101-tutorial

啟動後有本電子書，照著做一遍！超讚！


## docker

```
docker run -dp 3000:3000 -v todo-db:/etc/todos docker-101
docker ps
docker stop <id>
```


## docker-compose

```
docker-compose up -d
docker-compose down
```

## 說明

本範例使用了 react.js/babel/nodemon 等技術，不管是 server 端或 client 端，只要程式一有修改，就會自動重建，立即可以檢視網站。

對應 nodemon 的，deno 應使用 denon

* [強型闖入DenoLand 29 - 去標籤密技](https://ithelp.ithome.com.tw/articles/10253470)

## log

docker

```
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED       STATUS       PORTS      
                         NAMES
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   5 hours ago   Up 5 hours   0.0.0.0:80->80/tcp, :::80->80/tcp   epic_colden
wsl> docker run -dp 3000:3000 -v todo-db:/etc/todos docker-101
8c6e3d09074c6b7a2d63960d75cb7923149860dd7afb2364d32cc21e3664f42d
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED          STATUS          PORTS                                       NAMES
8c6e3d09074c   docker-101                   "docker-entrypoint.s…"   17 seconds ago   Up 16 seconds   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   xenodochial_pare
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   5 hours ago      Up 5 hours      0.0.0.0:80->80/tcp, :::80->80/tcp           epic_colden
wsl> docker stop 8c6e
8c6e
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED       STATUS       PORTS      
                         NAMES
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   5 hours ago   Up 5 hours   0.0.0.0:80->80/tcp, :::80->80/tcp   epic_colden
wsl> docker rm 8c6e
8c6e
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED       STATUS       PORTS      
                         NAMES
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   5 hours ago   Up 5 hours   0.0.0.0:80->80/tcp, :::80->80/tcp   epic_colden
wsl> docker images
REPOSITORY                   TAG         IMAGE ID       CREATED         SIZE
ccckmit/101-todo-app         latest      8af41e3fdad7   3 hours ago     171MB
docker-101                   latest      8af41e3fdad7   3 hours ago     171MB
<none>                       <none>      3e812642a04f   3 hours ago     171MB
postgres                     alpine      b8c450ae0903   4 days ago      192MB
denoland/deno                latest      c6678f922d2c   8 days ago      170MB
gitea/gitea                  latest      7737d8e9cae8   10 days ago     148MB
nginx                        latest      dd34e67e3371   2 weeks ago     133MB
mysql                        5.7         6c20ffa54f86   2 weeks ago     448MB
mysql                        latest      5a4e492065c7   2 weeks ago     514MB
node                         10-alpine   aa67ba258e18   4 months ago    82.7MB
dockersamples/101-tutorial   latest      45328bdf05eb   21 months ago   25.8MB
```


docker-compose

```
wsl> docker-compose up -d
Creating network "app_default" with the default driver
Creating app_app_1   ... done
Creating app_mysql_1 ... done
```
