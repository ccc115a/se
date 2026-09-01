# ps

ps fax // 印出行程樹

```
wsl> docker ps
CONTAINER ID   IMAGE                        COMMAND                  CREATED         STATUS          PORTS
                     NAMES
adc423525ae5   dockersamples/101-tutorial   "nginx -g 'daemon of…"   3 seconds ago   Up 2 seconds    0.0.0.0:80->80/tcp, :::80->80/tcp                   epic_colden
7bc99817bf6e   postgres:alpine              "docker-entrypoint.s…"   19 hours ago    Up 33 minutes   5432/tcp
                     gitea-postgres_db_1
eedb8d6b7be5   gitea/gitea:latest           "/usr/bin/entrypoint…"   19 hours ago    Up 33 minutes   22/tcp, 0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   gitea-postgres_gitea_1

wsl> ps fax
  PID TTY      STAT   TIME COMMAND
    1 ?        Sl     0:00 /init
   45 ?        Ss     0:00 /init
   46 ?        S      0:00  \_ /init
   47 pts/0    Ssl+   0:00  |   \_ /mnt/wsl/docker-desktop/docker-desktop-proxy --distro-name Ubuntu-20.04 --docker-desktop-root /mn   48 ?        Z      0:00  \_ [init] <defunct>
   55 ?        Z      0:00  \_ [init] <defunct>
   63 ?        Z      0:00  \_ [init] <defunct>
   65 ?        Z      0:00  \_ [init] <defunct>
   67 ?        Z      0:00  \_ [init] <defunct>
   74 ?        Z      0:00  \_ [init] <defunct>
   76 ?        Z      0:00  \_ [init] <defunct>
   78 ?        Z      0:00  \_ [init] <defunct>
   85 ?        Z      0:00  \_ [init] <defunct>
   87 ?        Z      0:00  \_ [init] <defunct>
   89 ?        Z      0:00  \_ [init] <defunct>
   96 ?        Z      0:00  \_ [init] <defunct>
   98 ?        Z      0:00  \_ [init] <defunct>
  101 ?        Z      0:00  \_ [init] <defunct>
  103 ?        Z      0:00  \_ [init] <defunct>
  105 ?        Z      0:00  \_ [init] <defunct>
  107 ?        S      0:00  \_ /init
  108 pts/1    Ssl+   0:00      \_ docker serve --address unix:///home/ccckmit/.docker/run/docker-cli-api.sock
  137 ?        Ss     0:00 /init
  138 ?        S      0:00  \_ /init
  139 pts/2    Ss     0:00      \_ -bash
  367 pts/2    R+     0:00          \_ ps fax
```
