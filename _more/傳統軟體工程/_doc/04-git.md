## 第 4 章 -- Git 合作

## 基本的 git 指令

指令       | 說明                                | 補充
----------|-------------------------------------|------------------------------------------------------
clone     | 複製某倉庫                            | git clone https://github.com/ccccourse/se.git 
init      | 創建新的 git 倉庫                     | git init
config    | 進行 git 帳號設定                     | git config --global user.email "xxxxx@gmail.com"  (或 user.name)
add       | 加入檔案到索引                         | git add -A (或用 * 加入本資料夾的檔案) 
commit    | 將檔案提交到儲存庫                     | git commit -m "xxxxxxxx" (--amend 可以再次提交, 蓋掉上一個) 
push      | 將版本推到遠端倉庫                     | git push origin master 
pull      | 從遠端將版本拉下來                     | git pull origin master
branch    | 建立一個新的分支(但不會切換到該分支)。    | git branch testing ; git branch (列出所有 branch)
remote    | 對遠端進行動作                         | git remote -v; git remote add ... 
fetch     | 取得遠端庫藏                          | git fetch upstream 
merge     | 合併另一分支                          | git merge test
stash     | 暫時儲藏修改                          | git stash; git stash list; git stash apply

* [陳鍾誠課程所必會的 git 的用法](https://gitlab.com/ccckmit/course/wikis/%E9%99%B3%E9%8D%BE%E8%AA%A0/%E6%8A%80%E8%83%BD/git)
* [常用 Git 命令清单](https://www.ruanyifeng.com/blog/2015/12/git-cheat-sheet.html) , 阮一峰.

## 用 git+github 合作

Git 是很好用的版本管理系統，而 Github 則是 Git 的專案大倉庫，包含了全世界的開放原始碼專案，我們可以透過 Git + Github 將專案發布在網路上，讓全世界的人都可以看到你的作品。

另外、我們可以透過 Git + Github 進行專案下載、修改、測試、發佈的動作，只要使用 git clone 就可以下載專案，然後修改測試完畢之後，再用

```
$ git add -A
$ git commit -m "xxxx"
$ git push origin master 
```

就能將專案推回 github 上。

對於兩人以上的專案，我們可以採用 Git + Github 進行合作，合作的方式有很多種，以下是常見的幾種：

1. 使用 fork + pull request 的方式進行協作
2. 將開發成員加入 collaborator ，然後用 git branch 的方式開發分支版本，完成後再合併回 master

在本章中，我們將先學習 github 的用法，然後再學習 git 的 branch 與 merge ，最後完整的使用 fork + pull request 的合作方法。


### 1. github 的初體驗

參考這篇 -- https://guides.github.com/activities/hello-world/

* 但是改成創建 mylodash2 專案！
    * 專案主：先創建一個 organization，例如 xxx108a
    * 專案主：在 organization 內創建 mylodash2 專案，勾選 README.md
    * 專案主：修改 README.md 放入專案描述資訊
    * 貢獻者：創建一個 readme-edits 分支
    * 貢獻者：修改 readme-edits 分支中的 README.md 後 commit 儲存 
    * 貢獻者：然後發送 pull request 給 master
    * 專案主：最後在 pull-request 裏檢視 file-changed, 若沒問題就收下該 pull-request !

### 2. 真正的專案合作

* 請先閱讀這篇 -- [Git 工作流程](http://www.ruanyifeng.com/blog/2015/12/git-workflow.html) , 阮一峰.

接著我們開始用 github flow 開發 mylodash 專案！

* 前置作業： 先創建一個新的 Organization，例如 (ccc108a)
* 狀況一： Owner 自己開發 : 
    * 在 organization 裏先創建一個 mylodash 專案。
    * 開始加入第一個函數 (例如 chunk)，並撰寫測試。
    * 寫好測好之後 commit 回 github
* 狀況二: 有團隊成員 member 不 fork 的情況下開發專案
    * 團隊成員寫第二個函數 (例如 concat) ，此時該團隊成員不能假設程式一定會成功完成，因此應該先創建一個新分支，例如就叫 add-concat。
    * 當我們寫好測試完成並推回 github 的 add-concat 版本後，發送 pull-request 給 master
    * 接著從 master 創建新測試分支 (ex: test-concat)，合併 add-concat 進行測試，如果沒問題就接受 merge 到 master 當中。
* 狀況三: 先 fork 的情況下開發專案
    * 參與者 fork 了 organization 的專案到自己帳號之後，加了一個新的函數 (ex: compact) ，然後送 pull-request 給 Owner 。
    * Owner 必須先 fetch 參與者的分支，然後創建新分支去合併並測試，如果成功的話再併入 master 分支。

上述三種狀況的詳細操作過程請點選下列連結：


* [老師 mylodash 專案之操作示範](./mylodash)

上課操作記錄

```
  502  mocha
  503  git branch
  504  git checkout -b add_chunk2
  505  git branch
  506  git add -A
  507  git commit -m "add chunk function"
  508  git push origin add_chunk2
```

* 另一個案例可以參考 [本頁舊版](https://gitlab.com/ccckmit/course/wikis/%E9%99%B3%E9%8D%BE%E8%AA%A0/%E6%9B%B8%E7%B1%8D/%E8%BB%9F%E9%AB%94%E5%B7%A5%E7%A8%8B/04-git?version_id=1c22456c2e5e55c5b16150067763607ec2688471) !

## 進階閱讀

* [陳鍾誠課程所必會的 git 的用法](https://gitlab.com/ccckmit/course/wikis/%E9%99%B3%E9%8D%BE%E8%AA%A0/%E6%8A%80%E8%83%BD/git)
* https://hackernoon.com/top-5-free-courses-to-learn-git-and-github-best-of-lot-2f394c6533b0
* https://kevintshoemaker.github.io/StatsChats/GIT_tutorial.html
* [Pro Git 中文版](https://git-scm.com/book/zh-tw/v2) 或 [English Version](https://git-scm.com/book/en/v2)
* [常用 Git 命令清单](https://www.ruanyifeng.com/blog/2015/12/git-cheat-sheet.html) , 阮一峰.
* [Git 工作流程](http://www.ruanyifeng.com/blog/2015/12/git-workflow.html) , 阮一峰.

## 參考文獻

* [本頁舊版](https://gitlab.com/ccckmit/course/wikis/%E9%99%B3%E9%8D%BE%E8%AA%A0/%E6%9B%B8%E7%B1%8D/%E8%BB%9F%E9%AB%94%E5%B7%A5%E7%A8%8B/04-git?version_id=1c22456c2e5e55c5b16150067763607ec2688471)
* https://guides.github.com/activities/hello-world/
* https://guides.github.com/activities/forking/