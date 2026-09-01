# deno git server

https://github.com/taisukef/deno-git-server


## server

```
deno run -A --unstable https://taisukef.github.io/deno-git-server/GitServer.js
```

## client

```
PS D:\pmedia\陳鍾誠\課程\網站設計進階\C1-gitcms\01-gitserver> cd test
PS D:\pmedia\陳鍾誠\課程\網站設計進階\C1-gitcms\01-gitserver\test> git add .
PS D:\pmedia\陳鍾誠\課程\網站設計進階\C1-gitcms\01-gitserver\test> git commit -m "add test.md"
[master (root-commit) c31a16c] add test.md
 1 file changed, 0 insertions(+), 0 deletions(-)     
 create mode 100644 test.md
PS D:\pmedia\陳鍾誠\課程\網站設計進階\C1-gitcms\01-gi7005/test
tserver\test> git push --set-upstream origin master  
Enumerating objects: 3, done.
Counting objects: 100% (3/3), done.
Writing objects: 100% (3/3), 202 bytes | 22.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 
To http://localhost:7005/test
 * [new branch]      master -> master
Branch 'master' set up to track remote branch 'master' from 'origin'.
PS D:\pmedia\陳鍾誠\課程\網站設計進階\C1-gitcms\01-gitserver\test> cd ..
PS D:\pmedir repo誠\課程\網站設計進階\C1-gitcms\01-gitserver>


    目錄: D:\pmedia\陳鍾誠\課程\網站設計進階\C1-gitcms\01-gitserver\repo   


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----       2021/8/16  上午 09:35                test.git

```