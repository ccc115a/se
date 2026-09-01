# gitea

## postgresql 設定

```
wsl> createdb gitea
wsl> psql gitea
psql (13.4 (Ubuntu 13.4-1.pgdg20.04+1))
Type "help" for help.
wsl> createuser -P -s -e cccpg
Enter password for new role: 
Enter it again: 
SELECT pg_catalog.set_config('search_path', '', false);
CREATE ROLE cccpg PASSWORD 'md568270cb105609182c85f7901ce3a8304' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN; 
```

## setting

網站標題:陳鍾誠的 gitea

儲存庫的根目錄
/mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea/data/gitea-repositories

Git LFS 根目錄
/mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea/data/lfs

Gitea HTTP 埠: 3333

Gitea 基本 URL: http://localhost:3333/

日誌路徑
/mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea/log

管理員帳號: ccckmit

## run on wsl

```
wsl> ./gitea web
2021/08/31 09:10:18 cmd/web.go:102:runWeb() [I] Starting Gitea on PID: 17415
2021/08/31 09:10:18 ...s/setting/setting.go:570:NewContext() [W] Custom config '/mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea/custom/conf/app.ini' not found, ignore this if you're running first time
2021/08/31 09:10:18 ...s/install/setting.go:21:PreloadSettings() [I] AppPath: /mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea/gitea
2021/08/31 09:10:18 ...s/install/setting.go:22:PreloadSettings() [I] AppWorkPath: /mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea
2021/08/31 09:10:18 ...s/install/setting.go:23:PreloadSettings() [I] Custom path: /mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea/custom
2021/08/31 09:10:18 ...s/install/setting.go:24:PreloadSettings() [I] Log path: /mnt/wsl/docker-desktop-bind-mounts/Ubuntu-20.04/fdbd7e23af76ca956070b6eadda658eaefba4c755edccae5481002971e28d70b/gitea/log
2021/08/31 09:10:18 ...s/install/setting.go:25:PreloadSettings() [I] Preparing to run install page
2021/08/31 09:10:20 cmd/web.go:196:listen() [I] Listen: http://0.0.0.0:3000
2021/08/31 09:10:20 ...s/graceful/server.go:62:NewServer() [I] Starting new Web server: tcp:0.0.0.0:3000 on PID: 17415
2021/08/31 09:11:03 ...ers/common/logger.go:21:1() [I] Started GET / for [::1]:44434
2021/08/31 09:11:03 ...ers/common/logger.go:30:1() [I] Completed GET / 200 OK in 11.8089ms
2021/08/31 09:11:03 ...ers/common/logger.go:21:1() [I] Started GET /assets/css/index.css?v=a3b76896522a66cc0564556e6ad7a83d for [::1]:44434
2021/08/31 09:11:03 ...ers/common/logger.go:21:1() [I] Started GET /assets/img/loading.png for [::1]:44432
2021/08/31 09:11:03 ...ers/common/logger.go:21:1() [I] Started GET /assets/js/index.js?v=a3b76896522a66cc0564556e6ad7a83d for [::1]:44436
2021/08/31 09:11:03 ...ers/common/logger.go:30:1() [I] Completed GET /assets/img/loading.png 200 OK in 11.6846ms
2021/08/31 09:11:03 ...ers/common/logger.go:30:1() [I] Completed GET /assets/css/index.css?v=a3b76896522a66cc0564556e6ad7a83d 200 OK in 14.5464ms
2021/08/31 09:11:03 ...ers/common/logger.go:30:1() [I] Completed GET /assets/js/index.js?v=a3b76896522a66cc0564556e6ad7a83d 200 OK in 3.115ms
2021/08/31 09:11:04 ...ers/common/logger.go:21:1() [I] Started GET /assets/img/favicon.png for [::1]:44436
2021/08/31 09:11:04 ...ers/common/logger.go:30:1() [I] Completed GET /assets/img/favicon.png 200 OK in 1.7285ms
2021/08/31 09:11:04 ...ers/common/logger.go:21:1() [I] Started GET /assets/img/logo.svg for [::1]:44436
2021/08/31 09:11:04 ...ers/common/logger.go:30:1() [I] Completed GET /assets/img/logo.svg 200 OK in 1.8004ms
2021/08/31 09:11:04 ...ers/common/logger.go:21:1() [I] Started GET /assets/serviceworker.js for [::1]:44436
2021/08/31 09:11:04 ...ers/common/logger.go:30:1() [I] Completed GET /assets/serviceworker.js 200 OK in 1.7289ms
```

## install on wsl

要安裝 node.js, golang, npm, postgresql

https://www.postgresql.org/download/linux/ubuntu/

```
  460  sudo apt install npm
  461  sudo apt update
  462  sudo apt install npm
  463  nvm
  464  sudo apt-get install curl
  465  curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
  466  node
  467  node -v
  468  curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
  469  sudo apt-get install nodejs
  470  node -v
  471  history
472  pwd
  473  TAGS="bindata" make build
  474  sudo npm install npm -g
  475  make clean
  476  TAGS="bindata" make build
  477  sudo npm i -g webpack-cli
  478  TAGS="bindata" make build
  479  go --version
  480  go -v
  481  go version
  482  rm -rf /usr/local/go && tar -C /usr/local -xzf go1.17.linux-amd64.tar.gz
  483  go version
  484  sudo add-apt-repository ppa:evarlast/golang1.4
  485  sudo apt-get update
  486  sudo add-apt-repository ppa:evarlast/golang1.17
  487  sudo apt-get update
  488  sudo apt-get install golang
  489  go version
  490  TAGS="bindata" make build
  491  pwd
  492  cd ..
  493  ls
  494  ls
  495  rm -rf /usr/local/go && tar -C /usr/local -xzf go1.17.linux-amd64.tar.gz
  496  sudo rm -rf /usr/local/go && tar -C /usr/local -xzf go1.17.linux-amd64.tar.gz
  497  sudo rm -rf /usr/local/go
  498  sudo tar -C /usr/local -xzf go1.17.linux-amd64.tar.gz
  499  export PATH=$PATH:/usr/local/go/bin
  500  vim ~/.bash_profile
  501  source ~/.bash_profile
  502  ls
  503  echo $PATH
  504  go version
  505  TAGS="bindata" make build
  506  cd gitea
  507  TAGS="bindata" make build
  508  history
wsl>
```
