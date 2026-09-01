# git / github 的用法

## 安裝

* 到 https://git-scm.com/downloads 下載 git 軟體並安裝
* 打入 git 指令，應該會出現下列訊息

```
$ git
usage: git [--version] [--help] [-C <path>] [-c name=value]
           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
           [-p | --paginate | --no-pager] [--no-replace-objects] [--bare]
           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
           <command> [<args>]

...
``` 

## 基本用法

下載專案

```
$ git clone https://github.com/xxxxxxx/xxx.git
... 若你是修改後還要推回的，xxxxxxx 應該是你自己的帳號 ...
... 若只是要 clone 老師的，那 xxxxxx 應該是 cccnqu ...

$ cd xxx  註: 切換到 clone 的資料夾 xxx 當中
```

... 接著加入一些新檔案，或者修改某些檔案後 ...

將專案推回

```
$ git add -A
$ git commit -m "xxxxxxxx"
$ git push origin master
Username : xxxxxx    <-- 輸入你的帳號 (github 上的)
Password :           <-- 輸入你的密碼
注意：在 Password 裡你打任何字，都不會印出來 (也不會印 * 號)，這是正常的。 (不要覺得為何打了沒反應 ....)
...
```

如果你是第一次在自己電腦上用 git push，那麼必須要先設定自己的 email 和 name， name 必須是 github 上的帳號。

```
$ git config --global user.email "xxxxx@gmail.com"
$ git config --global user.name "xxxxx"
```

## git push 失敗時的處理

在 Mac 上若沒問密碼且推不上去，很可能是裡面已經有設 ssh 證書，請用下列指令清掉。

```
$ git credential-osxkeychain erase
host=github.com
protocol=https
<press return>
```

如果 github 上的版本比你 local 的新，那麼可能會有訊息提示，此時可以用 pull 把遠端新的資料拉下來，指令如下：

```
$ git pull origin master
```

在 WINDOWS 底下，可以用 控制台\所有控制台項目\認證管理員\WINDOWS 認證 去刪除 GITHUB 的證書，然後再重新 push 就行了!

## 與老師的專案同步

* https://gist.github.com/CristinaSolana/1885435

```
$ git remote add upstream git://github.com/cccnqu/wd106b.git
$ git fetch upstream
$ git pull upstream master
```

再推回你自己的 github 中

```
$ git push origin master
```

## 用 github 架站 -- github pages

最新作法請參考 -- https://pages.github.com/

以下是舊的做法，應該還是可以用：

到你 github 專案的 setting (例如 https://github.com/ccckmit/wd107b/settings ) 裏，找到 GitHub Pages 那一段，在 source 點選成 master branch ，然後該頁會從新整理後，出現一個像 https://ccckmit.github.io/wd107b/ 這樣的網址，這樣你的網站就公開在網路上了。

接著將路徑（例如exercise/ccc.html）補在公開站後面，變成 https://ccckmit.github.io/wd107b/exercise/ccc.html ，這樣就可以看到網頁了！

## 圖形介面

* [GitKraken – 好用的垮平台Git GUI](https://wordpress.lokidea.com/blog/1624/gitkraken-%E5%A5%BD%E7%94%A8%E7%9A%84%E5%9E%AE%E5%B9%B3%E5%8F%B0git-gui/)

## 合作開發

使用 fork 之後，必須將對方設為 upstream 才能更新

```
$ git remote add upstream https://github.com/ccc-js/pos.git

$ git remote -v
origin  https://github.com/ccckmit/pos.git (fetch)
origin  https://github.com/ccckmit/pos.git (push)
upstream        https://github.com/ccc-js/pos.git (fetch)
upstream        https://github.com/ccc-js/pos.git (push)

$ git fetch upstream
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (1/1), done.
From https://github.com/ccc-js/pos
   e5bb420..85730a0  master     -> upstream/master

$ git checkout uptream/master
Switched to branch 'uptream/master'

$ git checkout -b developLoginUi
Switched to a new branch 'developLoginUi'

$ git status
On branch developLoginUi
nothing to commit, working tree clean

然後完成 developLoginUi，之後用

$ git push origin developLoginUi 推回自己的 repository

接著發送 pull request 請求合併！
```

## 更深入的 git 教學資源

* [Pro Git book 簡體中文版](https://git-scm.com/book/zh/v2)
* [Yodalee 的 Git 教學影片系列](http://yodalee.blogspot.tw/2017/12/git-video.html?m=1)
* [陳鍾誠的軟體工程課 -- Git 指南](https://github.com/cccnqu/se106a/wiki/git.md)
* [陳鍾誠的軟體工程課 -- Github 指南](https://github.com/cccnqu/se106a/wiki/github.md)
* [利用 Github Classroom 加 Travis CI 打造改作業系統](https://blog.techbridge.cc/2018/02/03/github-classroom-and-travis-ci/)

