# docker101

## souce code

static/index.html

```html

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no, maximum-scale=1.0, user-scalable=0" />
    <link rel="stylesheet" href="css/bootstrap.min.css" crossorigin="anonymous" />
    <link rel="stylesheet" href="css/font-awesome/all.min.css" crossorigin="anonymous" />
    <link href="https://fonts.googleapis.com/css?family=Lato&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="css/styles.css" />
    <title>Todo App</title>
</head>
<body>
    <div id="root"></div>
    <script src="js/react.production.min.js" integrity="sha256-3vo65ZXn5pfsCfGM5H55X+SmwJHBlyNHPwRmWAPgJnM=" crossorigin="anonymous"></script>
    <script src="js/react-dom.production.min.js" integrity="sha256-qVsF1ftL3vUq8RFOLwPnKimXOLo72xguDliIxeffHRc=" crossorigin="anonymous"></script>
    <script src="js/react-bootstrap.js" integrity="sha256-6ovUv/6vh4PbrUjYfYLH5FRoBiMfWhR/manIR92XEws=" crossorigin="anonymous"></script>
    <script src="js/babel.min.js" integrity="sha256-FiZMk1zgTeujzf/+vomWZGZ9r00+xnGvOgXoj0Jo1jA=" crossorigin="anonymous"></script>
    <script type="text/babel" src="js/app.js"></script>
</body>
</html>
```

其中的 react.production.min.js babel.min.js 這些東西，只要前端有改，就會被重新 render。


## compose

```
wsl> docker-compose up -d
Creating network "app_default" with the default driver
Creating volume "app_todo-mysql-data" with default driver
Pulling app (node:10-alpine)...
10-alpine: Pulling from library/node
ddad3d7c1e96: Already exists
de915e575d22: Already exists
7150aa69525b: Already exists
d7aa47be044e: Already exists
Digest: sha256:dc98dac24efd4254f75976c40bce46944697a110d06ce7fa47e7268470cf2e28
Status: Downloaded newer image for node:10-alpine
Pulling mysql (mysql:5.7)...
5.7: Pulling from library/mysql
e1acddbe380c: Already exists
bed879327370: Already exists
03285f80bafd: Already exists
ccc17412a00a: Already exists
1f556ecc09d1: Already exists
adc5528e468d: Already exists
1afc286d5d53: Already exists
4d2d9261e3ad: Pull complete
ac609d7b31f8: Pull complete
53ee1339bc3a: Pull complete
b0c0a831a707: Pull complete
Digest: sha256:7cf2e7d7ff876f93c8601406a5aa17484e6623875e64e7acc71432ad8e0a3d7e
Status: Downloaded newer image for mysql:5.7
Creating app_app_1 ... 
Creating app_app_1   ... error
WARNING: Host is already in use by another container

ERROR: for app_app_1  Cannot start service app: driver failed programming external connectivity on endpoint app_app_1 (4388fb9f1d03bCreating app_mysql_1 ... done

ERROR: for app  Cannot start service app: driver failed programming external connectivity on endpoint app_app_1 (4388fb9f1d03b80b29ec2d88787542556c9ee333cc3ff981ccda1a8504998640): Bind for 0.0.0.0:3000 failed: port is already allocated
ERROR: Encountered errors while bringing up the project.
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
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED          STATUS          PORTS
              NAMES
86fb83f04b33   mysql:5.7                    "docker-entrypoint.s…"   15 seconds ago   Up 12 seconds   3306/tcp, 33060/tcp
              app_mysql_1
3f780b895cc9   docker-101                   "docker-entrypoint.s…"   2 hours ago      Up 2 hours      0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   zen_spence
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   5 hours ago      Up 5 hours      0.0.0.0:80->80/tcp, :::80->80/tcp           epic_colden
wsl> docker rm 3f78
Error response from daemon: You cannot remove a running container 3f780b895cc9f89ed59e93057b685bfc8f49ac41442ff6718e58465134a69750. 
Stop the container before attempting removal or force remove
wsl> docker stop 3f78
3f78
wsl> docker rm 3f78
3f78
wsl> docker-compose up -d
Starting app_app_1 ... 
Starting app_app_1 ... done
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED              STATUS              PORTS
                      NAMES
392ac01ca352   node:10-alpine               "docker-entrypoint.s…"   About a minute ago   Up 10 seconds       0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   app_app_1
86fb83f04b33   mysql:5.7                    "docker-entrypoint.s…"   About a minute ago   Up About a minute   3306/tcp, 33060/tcp   
                      app_mysql_1
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   5 hours ago          Up 5 hours          0.0.0.0:80->80/tcp, :::80->80/tcp           epic_colden
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
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED         STATUS         PORTS
            NAMES
392ac01ca352   node:10-alpine               "docker-entrypoint.s…"   3 minutes ago   Up 2 minutes   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   app_app_1
86fb83f04b33   mysql:5.7                    "docker-entrypoint.s…"   3 minutes ago   Up 3 minutes   3306/tcp, 33060/tcp
            app_mysql_1
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   5 hours ago     Up 5 hours     0.0.0.0:80->80/tcp, :::80->80/tcp           epic_colden
wsl> docker logs -f 392a
yarn install v1.22.5
[1/4] Resolving packages...
[2/4] Fetching packages...
info "fsevents@1.2.9" is an optional dependency and failed compatibility check. Excluding it from installation.                                                                                                       ion.
[3/4] Linking dependencies...
[4/4] Building fresh packages...
Done in 77.22s.
yarn run v1.22.5
$ nodemon src/index.js
[nodemon] 1.19.2
[nodemon] to restart at any time, enter `rs`
[nodemon] watching dir(s): *.*
[nodemon] starting `node src/index.js`
Waiting for mysql:3306.
Connected!
Connected to mysql db at host mysql
Listening on port 3000
```

## note

```
docker build -t docker-101 .

docker images

docker run -dp 3000:3000 docker-101

-d: detached mode

-p: port
```

## database

app/src/persistence

```js
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const location = process.env.SQLITE_DB_LOCATION || '/etc/todos/todo.db';
```

```
$ docker volume create todo-db
$ docker run -dp 3000:3000 -v todo-db:/etc/todos docker-101
```

## log

```
$ wsl
wsl> cd app
wsl> ls
package.json  spec  src  yarn.lock
wsl> docker build -t docker-101 .
[+] Building 66.4s (9/9) FINISHED
 => [internal] load build definition from Dockerfile                                                          0.1s 
 => => transferring dockerfile: 154B                                                                          0.0s 
 => [internal] load .dockerignore                                                                             0.0s 
 => => transferring context: 2B                                                                               0.0s 
 => [internal] load metadata for docker.io/library/node:10-alpine                                            12.6s 
 => [1/4] FROM docker.io/library/node:10-alpine@sha256:dc98dac24efd4254f75976c40bce46944697a110d06ce7fa47e7  23.0s 
 => => resolve docker.io/library/node:10-alpine@sha256:dc98dac24efd4254f75976c40bce46944697a110d06ce7fa47e72  0.0s 
 => => sha256:de915e575d22c7e33c83fddaf7aee0672e5d6a67e598a26fe0b30c7022f53cdd 22.21MB / 22.21MB             19.4s 
 => => sha256:7150aa69525b95f82b3df6a61a002f82382b2f3ea8ce51b9000b965f7476a5cc 2.35MB / 2.35MB                2.2s 
 => => sha256:d7aa47be044e5a988e3e7f204e2e28cb9f070daa32ed081072ad6d5bf6c085d1 280B / 280B                    1.1s 
 => => sha256:dc98dac24efd4254f75976c40bce46944697a110d06ce7fa47e7268470cf2e28 1.65kB / 1.65kB                0.0s 
 => => sha256:02767d92553e465bf51e0bd661074f2e70bd575c4a69a0d610aa6e78fd20a9bf 1.16kB / 1.16kB                0.0s 
 => => sha256:aa67ba258e1877ed6ec455a7f4cc69e25cf0f0b027a7f6f3c63a8eca2c8a440c 6.73kB / 6.73kB                0.0s 
 => => extracting sha256:de915e575d22c7e33c83fddaf7aee0672e5d6a67e598a26fe0b30c7022f53cdd                     2.8s 
 => => extracting sha256:7150aa69525b95f82b3df6a61a002f82382b2f3ea8ce51b9000b965f7476a5cc                     0.3s 
 => => extracting sha256:d7aa47be044e5a988e3e7f204e2e28cb9f070daa32ed081072ad6d5bf6c085d1                     0.0s 
 => [internal] load build context                                                                             0.7s 
 => => transferring context: 4.64MB                                                                           0.7s 
 => [2/4] WORKDIR /app                                                                                        0.5s 
 => [3/4] COPY . .                                                                                            0.1s 
 => [4/4] RUN yarn install --production                                                                      26.8s 
 => exporting to image                                                                                        3.2s 
 => => exporting layers                                                                                       3.2s 
 => => writing image sha256:3e812642a04fd8d680bbb05ce1c1eb64d5a9f5eba75a7b4c8cd2fa7ee81a9c7e                  0.0s 
 => => naming to docker.io/library/docker-101                                                                 0.0s 

Use 'docker scan' to run Snyk tests against images to find vulnerabilities and learn how to fix them
wsl> docker run -dp 3000:3000 docker-101
87757fdc703cfbdae5a16e1bbb119d845f14e5d5d864504f75b6c9b1eaf3a9da
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED          STATUS          PORTS        
                               NAMES
87757fdc703c   docker-101                   "docker-entrypoint.s…"   11 seconds ago   Up 10 seconds   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   heuristic_joliot
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   2 hours ago      Up 2 hours      0.0.0.0:80->80/tcp, :::80->80/tcp           epic_colden

wsl> docker images
REPOSITORY                   TAG       IMAGE ID       CREATED         SIZE
docker-101                   latest    3e812642a04f   4 minutes ago   171MB
postgres                     alpine    b8c450ae0903   4 days ago      192MB
denoland/deno                latest    c6678f922d2c   8 days ago      170MB
gitea/gitea                  latest    7737d8e9cae8   10 days ago     148MB
nginx                        latest    dd34e67e3371   2 weeks ago     133MB
mysql                        latest    5a4e492065c7   2 weeks ago     514MB
dockersamples/101-tutorial   latest    45328bdf05eb   21 months ago   25.8MB
```