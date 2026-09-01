# docker-compose (gitea+postgresql)

來源 -- https://github.com/docker/awesome-compose/tree/master/gitea-postgres

```
$ wsl
wsl> docker-compose up -d
Creating network "gitea-postgres_default" with the default driver
Creating volume "gitea-postgres_db_data" with default driver
Creating volume "gitea-postgres_git_data" with default driver
Pulling db (postgres:alpine)...
alpine: Pulling from library/postgres
a0d0a0d46f8b: Pull complete
5034a66b99e6: Pull complete
82e9eb77798b: Pull complete
314b9347faf5: Pull complete
2625be9fae82: Pull complete
5ec8358e2a99: Pull complete
2e9ccfc29d86: Pull complete
2a4d94e5dde0: Pull complete
Digest: sha256:a70babcd0e8f86272c35d6efcf8070c597c1f31b3d19727eece213a09929dd55
Status: Downloaded newer image for postgres:alpine
Creating gitea-postgres_db_1    ... done
Creating gitea-postgres_gitea_1 ... done
wsl> docker ps
CONTAINER ID   IMAGE                COMMAND                  CREATED              STATUS              PORTS        
                                       NAMES
7bc99817bf6e   postgres:alpine      "docker-entrypoint.s…"   About a minute ago   Up About a minute   5432/tcp     
                                       gitea-postgres_db_1
eedb8d6b7be5   gitea/gitea:latest   "/usr/bin/entrypoint…"   About a minute ago   Up About a minute   22/tcp, 0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   gitea-postgres_gitea_1
```

## run

![](./run.png)


