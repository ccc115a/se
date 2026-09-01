# 用 docker compose 在 linode 上安裝 gitea

參考 -- https://docs.gitea.io/en-us/install-with-docker/

```
2021  git clone git@github.com:ccckmit/gitea.git
 2022  ls
 2023  cd gitea
 2024  ls
 2025  cat docker-compose.yml
 2026  docker-compose
 2027  apt install docker-compose
 2028  docker-compose
 2029  docker-compose up -d
 2030  docker
 2031  docker images
 2032  docker-compose down --rmi local
 2033  docker images
 2034  docker-compose up -d
 2035  ls
 2036  docker-compose down --rmi local
 2037  rm -rf gitea
 2038  ls
 2039  docker-compose up -d
 2040  ls
 2041  mkdir mygitea
 2042  cd mygitea
 2043  touch README.md
 2044  git init
 2045  git commit -m "first commit"
 2046  git add -A
 2047  git commit -m "first commit"
 2048  git remote add origin git@programmermedia.org:ccckmit/mygitea.git
 2049  git push origin master
 2050  history
 2051  cat /root/.ssh/id_rsa.pub
 2052  git push -u origin master
 2053  git push origin master
 2054  git remote -v
 2055  git remote rm origin
 2056  git remote -v
 2057  git remote add origin http://programmermedia.org:3000/ccckmit/mygitea.git
 2058  git push origin master
```
