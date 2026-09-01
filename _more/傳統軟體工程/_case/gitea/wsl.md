# wsl


```
wsl> docker run -d --name=gitea2 -p 22:22 -p 3000:3000 -v /var/lib/gitea:/data gitea/gitea:latest7358d962c0f6cb2f39cfffef5f112cf106ce838b6a3342b58ef606628901523itea/gitea:latest9
wsl> ls /var/lib/gitea
git  gitea  ssh
wsl> ls /var/lib/gitea/gitea
attachments  conf      indexers  log     repo-archive  sessions
avatars      gitea.db  jwt       queues  repo-avatars
wsl> ls /var/lib/gitea
git  gitea  ssh
wsl> ls /var/lib/gitea/git
lfs  repositories
wsl> ls /var/lib/gitea/git/repositories/
ccckmit
wsl> ls
wsl> ls /var/lib/gitea/git/repositories/ccckmit/
test1.git
wsl> ls /var/lib/gitea/git/repositories/ccckmit/test1.git
HEAD  branches  config  description  hooks  info  objects  refs
```

## install

* [How to Install Gitea on Ubuntu 20.04](https://linuxize.com/post/how-to-install-gitea-on-ubuntu-20-04/)


## 

```
$ wsl
wsl> createuser -P -s -e cccgitea
Enter password for new role:
Enter it again:
SELECT pg_catalog.set_config('search_path', '', false);
CREATE ROLE cccgitea PASSWORD 'md5620aecfb1941f338fc021c6e7b91ff68' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;   
```
