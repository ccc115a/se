# docker



## usage

```
docker images // 列出映像
docker search <keyword> // 搜尋映像
docker pull <image> // 下載映像
docker rmi <image> // 刪除映像 (加 -f 強制刪除)

docker run <image> // 執行映像，創建容器
docker start <image> // 啟動容器
docker ps // 印出正在執行的容器
docker kill <id>// 殺死正在執行的容器
docker restart <image> // 重啟容器
docker attach <image> // 連接容器
docker exec <image> // 運行命令 ex: docker exec hello echo "Hello World!" 
docker stop <image> // 終止容器 
docker rm <image> // 刪除容器
docker-compose  // 根據 docker-compose.yaml 組合出映像
```

## history


```
 1995  sudo apt-get remove docker docker-engine docker.io containerd runc
 1996  sudo apt-get update
 1997  sudo apt-get install     apt-transport-https     ca-certificates     curl     gnupg     lsb-release
 1998  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
 1999  echo   "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
 2000  sudo apt-get update
 2001  sudo apt-get install docker-ce docker-ce-cli containerd.io
 2002  sudo docker run hello-world
 2003  docker list
 2004  docker --help
 2005  docker images
 2006  sudo docker run hello-world
```