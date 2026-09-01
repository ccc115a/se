# githook

* [Git 什麼是Git Hooks？](https://matthung0807.blogspot.com/2021/08/what-is-git-hooks.html)
    * Git Hooks又分為client-side hooks及server-side hooks。client-side hooks為在client的操作如commit、merge、checkout會觸發，server-side hooks則是在push到遠端倉庫時會觸發。
* [從懶開始的自動化生活 : A little talk about Git Hooks](https://ithelp.ithome.com.tw/articles/10239676)
* [提升程式碼品質：使用 Pre-Commit (Git Hooks)](https://mropengate.blogspot.com/2019/08/pre-commit-git-hooks_4.html)


## 範例 Client Hook: pre-commit

在 .git/hooks 底下，加入 pre-commit 檔案，內容如下：

```
#!/bin/sh
echo Hello, Hook
# exit 1
```

commit

```
$ git commit -m "test hook"
Hello, Hook
```

這樣你每次做 git commit 時都會回應 Hello, Hook

若 exit 1 沒註解，則每次都會 commit 失敗。

## 範例 Client Hook: pre-commit

```
#!/bin/sh
deno fmt */*.ts */*.js
```

commit

```
$ git commit -m "format hook"
\\?\C:\ccc\course\sa110a_lodash\src\chunk.ts
Checked 11 files
[main 63349f9] format hook
 1 file changed, 1 insertion(+), 1 deletion(-)
```

