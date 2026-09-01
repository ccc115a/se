# mylodash 的 github pull request 練習

* 先看這兩張圖
    * https://hackernoon.com/top-5-free-courses-to-learn-git-and-github-best-of-lot-2f394c6533b0
    * https://kevintshoemaker.github.io/StatsChats/GIT_tutorial.html

## pull-request 初體驗

* 先創建一個 organization 機構
    * 例如 : https://github.com/ccccourse/
    * 請按《最右上角》菜單，然後選 setting，接著向下拉選 organization 後選 new organization .
    * 然後選 Team for Open Source ($0 USD), 填入 organization 與基本資料就好了！
* 在 organization 中創建一個 mylodash 專案
    * 請在 README.md 選項上打勾勾
    * 老師範例: https://github.com/ccccourse/mylodash
* fork 該專案到自己的帳號名下
    * 老師範例: https://github.com/ccckmit/mylodash
* 接著修改其 README.md 的內容，然後發送 pull-request 給原專案 (organization)
    * 然後讓 organization 接受該 pull-request。 
* 創建新版本，然後再次修改其 README.md 的內容，接著發送 pull-request 給原專案 (organization)
    * 然後讓 organization 接受該 pull-request。 

本階段成果 -- https://github.com/ccccourse/mylodash/commit/2579c5f8dcbe6a4bbfd6254042e7ff43dceccb22

## 主控者： 單人使用 git 有系統的開發程式

clone organization 的 mylodash 到本地 (如果已經 clone 過，就用 git pull origin master)

```
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git pull origin master
remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
remote: Compressing objects: 100% (6/6), done.
remote: Total 8 (delta 1), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (8/8), done.
From https://github.com/ccccourse/mylodash
 * branch            master     -> FETCH_HEAD
   4bd32dc..2579c5f  master     -> origin/master
Updating 4bd32dc..2579c5f
Fast-forward
 README.md | 7 ++++++-
 1 file changed, 6 insertions(+), 1 deletion(-)

```


用 git checkout 創建一個開發分支 (ex: add_chunk)

```
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git checkout -b add_chunk
 
```

新增一個 lodash 函數 (例如 chunk) ，然後測試直到通過為止

```
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]


  3 passing (34ms)
```

用 master 合併分支 (ex:add_chunk) ，合併完之後再測試一次

```
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git branch
* add_chunk
  master

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git checkout master
Deletion of directory 'test' failed. Should I try again? (y/n) n
Switched to branch 'master'
Your branch is up to date with 'origin/master'.

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git merge add_chunk
Updating 2579c5f..90969e2
Fast-forward
 src/chunk.js      |  9 +++++++++
 test/chunkTest.js | 14 ++++++++++++++
 2 files changed, 23 insertions(+)
 create mode 100644 src/chunk.js
 create mode 100644 test/chunkTest.js

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]


  3 passing (35ms)

```

確認主版沒問題之後，送回 github 

```
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git add -A
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git commit -m "add chunk and pass test"
[add_chunk 90969e2] add chunk and pass test
 2 files changed, 23 insertions(+)
 create mode 100644 src/chunk.js
 create mode 100644 test/chunkTest.js
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git push origin master
fatal: HttpRequestException encountered.
   傳送要求時發生錯誤。
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Counting objects: 6, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (4/4), done.
Writing objects: 100% (6/6), 738 bytes | 73.00 KiB/s, done.
Total 6 (delta 0), reused 0 (delta 0)
To https://github.com/ccccourse/mylodash.git
   2579c5f..90969e2  master -> master
```

本階段成果 -- https://github.com/ccccourse/mylodash/commit/90969e20c041f37b7eeea67fdfdfd6e9bb9712d3


## 貢獻者 : (專案成員) 不 fork 專案的貢獻程式的方法

clone organization 的 mylodash 到本地

```
PS D:\ccc\course\se\exercise\01-git\member> git clone https://github.com/ccccourse/mylodash.git
Cloning into 'mylodash'...
remote: Enumerating objects: 17, done.
remote: Counting objects: 100% (17/17), done.
remote: Compressing objects: 100% (12/12), done.
remote: Total 17 (delta 1), reused 6 (delta 0), pack-reused 0
Unpacking objects: 100% (17/17), done.
```


接著由於該 lodash 專案沒有 package.json，所以貢獻者乾脆幫主控者創造一個 (這不是正常現象)

```
PS D:\ccc\course\se\exercise\01-git\member\mylodash> npm init
npm WARN npm npm does not support Node.js v10.16.0
npm WARN npm You should probably upgrade to a newer version of node as we
npm WARN npm can't make any promises that npm will work with this version.
npm WARN npm Supported releases of Node.js are the latest release of 4, 6, 7, 8, 9.
npm WARN npm You can find the latest version at https://nodejs.org/
This utility will walk you through creating a package.json file.
It only covers the most common items, and tries to guess sensible defaults.

See `npm help json` for definitive documentation on these fields
and exactly what they do.

Use `npm install <pkg>` afterwards to install a package and
save it as a dependency in the package.json file.

Press ^C at any time to quit.
package name: (mylodash)
version: (1.0.0) 0.0.2
description: Remade lodash for exercise
entry point: (index.js) src/index.js
test command: mocha
git repository: (https://github.com/ccccourse/mylodash.git)
keywords: lodash
author: ccc
license: (ISC) MIT
About to write to D:\ccc\course\se\exercise\01-git\member\mylodash\package.json:

{
  "name": "mylodash",
  "version": "0.0.2",
  "description": "Remade lodash for exercise",
  "main": "src/index.js",
  "directories": {
    "test": "test"
  },
  "scripts": {
    "test": "mocha"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/ccccourse/mylodash.git"
  },
  "keywords": [
    "lodash"
  ],
  "author": "ccc",
  "license": "MIT",
  "bugs": {
    "url": "https://github.com/ccccourse/mylodash/issues"
  },
  "homepage": "https://github.com/ccccourse/mylodash#readme"
}


Is this ok? (yes) yes
PS D:\ccc\course\se\exercise\01-git\member\mylodash> npm i chai --save
npm WARN npm npm does not support Node.js v10.16.0
npm WARN npm You should probably upgrade to a newer version of node as we
npm WARN npm can't make any promises that npm will work with this version.
npm WARN npm Supported releases of Node.js are the latest release of 4, 6, 7, 8, 9.
npm WARN npm You can find the latest version at https://nodejs.org/
npm notice created a lockfile as package-lock.json. You should commit this file.
+ chai@4.2.0
added 7 packages in 5.923s
```

用 git checkout 創建一個開發分支 (ex: add_concat)

```
PS D:\ccc\course\se\exercise\01-git\member\mylodash> git checkout -b add_concat
Switched to a new branch 'add_concat'

PS D:\ccc\course\se\exercise\01-git\member\mylodash> git branch
* add_concat
  master

```

新增一個 lodash 函數 (例如 concat) 及其測試

```
PS D:\ccc\course\se\exercise\01-git\member\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  5 passing (61ms)

```

在測試過後將該分支 (ex: add_concat) push 回 organization 的 mylodash 中，然後發送 pull-request 給專案的 master 版本 

```

PS D:\ccc\course\se\exercise\01-git\member\mylodash> git add -A
PS D:\ccc\course\se\exercise\01-git\member\mylodash> git commit -m "add concat"
[add_concat e35d9b7] add concat
 5 files changed, 110 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 package-lock.json
 create mode 100644 package.json
 create mode 100644 src/concat.js
 create mode 100644 test/concatTest.js
PS D:\ccc\course\se\exercise\01-git\member\mylodash> git push origin add_concat
fatal: HttpRequestException encountered.
   傳送要求時發生錯誤。
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Counting objects: 9, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (8/8), done.
Writing objects: 100% (9/9), 1.93 KiB | 165.00 KiB/s, done.
Total 9 (delta 0), reused 0 (delta 0)
remote:
remote: Create a pull request for 'add_concat' on GitHub by visiting:
remote:      https://github.com/ccccourse/mylodash/pull/new/add_concat
remote:
To https://github.com/ccccourse/mylodash.git
 * [new branch]      add_concat -> add_concat
```

中間成果： https://github.com/ccccourse/mylodash/tree/add_concat

主控者將 master 與該分支 (ex: add_concat) 合併，然後再進行測試，若檢核通過的話，那麼就將該分支合併進

```
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git pull origin add_concat
remote: Enumerating objects: 12, done.
remote: Counting objects: 100% (12/12), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 9 (delta 0), reused 9 (delta 0), pack-reused 0
Unpacking objects: 100% (9/9), done.
From https://github.com/ccccourse/mylodash
 * branch            add_concat -> FETCH_HEAD
 * [new branch]      add_concat -> origin/add_concat
Updating 90969e2..e35d9b7
Fast-forward
 .gitignore         |  3 +++
 package-lock.json  | 54 ++++++++++++++++++++++++++++++++++++++++++++++++++++++
 package.json       | 28 ++++++++++++++++++++++++++++
 src/concat.js      |  9 +++++++++
 test/concatTest.js | 16 ++++++++++++++++
 5 files changed, 110 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 package-lock.json
 create mode 100644 package.json
 create mode 100644 src/concat.js
 create mode 100644 test/concatTest.js
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git checkout master
Already on 'master'
Your branch is ahead of 'origin/master' by 1 commit.
  (use "git push" to publish your local commits)

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git merge origin/add_concat

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git branch
  add_chunk
* master

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> npm i
npm WARN npm npm does not support Node.js v10.16.0
npm WARN npm You should probably upgrade to a newer version of node as we
npm WARN npm can't make any promises that npm will work with this version.
npm WARN npm Supported releases of Node.js are the latest release of 4, 6, 7, 8, 9.
npm WARN npm You can find the latest version at https://nodejs.org/
added 7 packages in 2.421s
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  5 passing (45ms)

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git push origin master
fatal: HttpRequestException encountered.
   傳送要求時發生錯誤。
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
remote: Invalid username or password.
fatal: Authentication failed for 'https://github.com/ccccourse/mylodash.git/'
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git push origin master
Logon failed, use ctrl+c to cancel basic credential prompt.
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Everything up-to-date
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git branch
  add_chunk
* master
```

## 貢獻者 : fork 專案之後貢獻程式的方法 (可能非成員，只是開放原始碼玩家)

clone 自己 fork 的 mylodash 到本地

```
PS D:\ccc\course\se\exercise\01-git\nonmember> git clone https://github.com/ccckmit/mylodash.git
Cloning into 'mylodash'...
remote: Enumerating objects: 26, done.
remote: Counting objects: 100% (26/26), done.
remote: Compressing objects: 100% (20/20), done.
remote: Total 26 (delta 1), reused 15 (delta 0), pack-reused 0
Unpacking objects: 100% (26/26), done.
PS D:\ccc\course\se\exercise\01-git\nonmember> cd mylodash
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> ls


    目錄: D:\ccc\course\se\exercise\01-git\nonmember\mylodash


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----      2019/9/16  下午 04:10                src
d-----      2019/9/16  下午 04:10                test
-a----      2019/9/16  下午 04:10             26 .gitignore
-a----      2019/9/16  下午 04:10           2023 package-lock.json
-a----      2019/9/16  下午 04:10            588 package.json
-a----      2019/9/16  下午 04:10            169 README.md
```

先測試一下該專案是否正常 (發現自己還沒安裝 chai) 於是打 npm i 安裝該專案需要的套件。

```
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> mocha
internal/modules/cjs/loader.js:638
    throw err;
    ^

Error: Cannot find module 'chai'
    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:636:15)
    at Function.Module._load (internal/modules/cjs/loader.js:562:25)
    at Module.require (internal/modules/cjs/loader.js:690:17)
    at require (internal/modules/cjs/helpers.js:25:18)
    at Object.<anonymous> (D:\ccc\course\se\exercise\01-git\nonmember\mylodash\test\concatTest.js:1:16)
    at Module._compile (internal/modules/cjs/loader.js:776:30)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:787:10)
    at Module.load (internal/modules/cjs/loader.js:653:32)
    at tryModuleLoad (internal/modules/cjs/loader.js:593:12)
    at Function.Module._load (internal/modules/cjs/loader.js:585:3)
    at Module.require (internal/modules/cjs/loader.js:690:17)
    at require (internal/modules/cjs/helpers.js:25:18)
    at C:\Users\user\AppData\Roaming\npm\node_modules\mocha\lib\mocha.js:231:27
    at Array.forEach (<anonymous>)
    at Mocha.loadFiles (C:\Users\user\AppData\Roaming\npm\node_modules\mocha\lib\mocha.js:228:14)
    at Mocha.run (C:\Users\user\AppData\Roaming\npm\node_modules\mocha\lib\mocha.js:536:10)
    at Object.<anonymous> (C:\Users\user\AppData\Roaming\npm\node_modules\mocha\bin\_mocha:582:18)
    at Module._compile (internal/modules/cjs/loader.js:776:30)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:787:10)
    at Module.load (internal/modules/cjs/loader.js:653:32)
    at tryModuleLoad (internal/modules/cjs/loader.js:593:12)
    at Function.Module._load (internal/modules/cjs/loader.js:585:3)
    at Function.Module.runMain (internal/modules/cjs/loader.js:829:12)
    at startup (internal/bootstrap/node.js:283:19)
    at bootstrapNodeJSCore (internal/bootstrap/node.js:622:3)
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> npm i
npm WARN npm npm does not support Node.js v10.16.0
npm WARN npm You should probably upgrade to a newer version of node as we
npm WARN npm can't make any promises that npm will work with this version.
npm WARN npm Supported releases of Node.js are the latest release of 4, 6, 7, 8, 9.
npm WARN npm You can find the latest version at https://nodejs.org/
added 7 packages in 2.53s
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  5 passing (52ms)
```

用 git checkout 創建一個開發分支 (ex: add_compact)

```
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> git branch
* master
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> git checkout -b add_compact
Switched to a new branch 'add_compact'
M       package-lock.json
M       package.json
```

新增一個 lodash 函數 (例如 compact) 及其測試

```
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  compact
    √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  6 passing (52ms)
```

在測試過後將該 add_compact 分支 push 回自己帳號的 mylodash 中

```
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> git add -A
warning: LF will be replaced by CRLF in package-lock.json.
The file will have its original line endings in your working directory.
warning: LF will be replaced by CRLF in package.json.
The file will have its original line endings in your working directory.
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> git commit -m "add compact and pass test"
[add_compact d06bcbc] add compact and pass test
 2 files changed, 17 insertions(+)
 create mode 100644 src/compact.js
 create mode 100644 test/compactTest.js
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> git branch
* add_compact
  master
PS D:\ccc\course\se\exercise\01-git\nonmember\mylodash> git push origin add_compact
fatal: HttpRequestException encountered.
   傳送要求時發生錯誤。
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Counting objects: 6, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (6/6), done.
Writing objects: 100% (6/6), 773 bytes | 85.00 KiB/s, done.
Total 6 (delta 1), reused 0 (delta 0)
remote: Resolving deltas: 100% (1/1), completed with 1 local object.
remote:
remote: Create a pull request for 'add_compact' on GitHub by visiting:
remote:      https://github.com/ccckmit/mylodash/pull/new/add_compact
remote:
To https://github.com/ccckmit/mylodash.git
 * [new branch]      add_compact -> add_compact
```

發送 pull request 給 organization 

```
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git remote add ccckmit https://github.com/ccckmit/mylodash.git
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git checkout -b ccckmit_compact
Switched to a new branch 'ccckmit_compact'

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git fetch ccckmit
remote: Enumerating objects: 9, done.
remote: Counting objects: 100% (9/9), done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 6 (delta 1), reused 6 (delta 1), pack-reused 0
Unpacking objects: 100% (6/6), done.
From https://github.com/ccckmit/mylodash
 * [new branch]      add_compact -> ccckmit/add_compact
 * [new branch]      add_concat  -> ccckmit/add_concat
 * [new branch]      master      -> ccckmit/master
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git branch
  add_chunk
* ccckmit_compact
  master
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git merge ccckmit/add_compact
Updating e35d9b7..d06bcbc
Fast-forward
 src/compact.js      | 9 +++++++++
 test/compactTest.js | 8 ++++++++
 2 files changed, 17 insertions(+)
 create mode 100644 src/compact.js
 create mode 100644 test/compactTest.js
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  compact
    √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  6 passing (53ms)

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git add -A
warning: LF will be replaced by CRLF in package-lock.json.
The file will have its original line endings in your working directory.
warning: LF will be replaced by CRLF in package.json.
The file will have its original line endings in your working directory.
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git commit -m "merge ccckmit/add_compact"
On branch ccckmit_compact
nothing to commit, working tree clean
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git checkout master
Switched to branch 'master'
Your branch is up to date with 'origin/master'.
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git branch
  add_chunk
  ccckmit_compact
* master
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git merge ccckmit_compact
Updating e35d9b7..d06bcbc
Fast-forward
 src/compact.js      | 9 +++++++++
 test/compactTest.js | 8 ++++++++
 2 files changed, 17 insertions(+)
 create mode 100644 src/compact.js
 create mode 100644 test/compactTest.js
PS D:\ccc\course\se\exercise\01-git\owner\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  compact
    √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  6 passing (52ms)

PS D:\ccc\course\se\exercise\01-git\owner\mylodash> git push origin master
fatal: HttpRequestException encountered.
   傳送要求時發生錯誤。
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Counting objects: 6, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (6/6), done.
Writing objects: 100% (6/6), 773 bytes | 96.00 KiB/s, done.
Total 6 (delta 1), reused 0 (delta 0)
remote: Resolving deltas: 100% (1/1), completed with 1 local object.
To https://github.com/ccccourse/mylodash.git
   e35d9b7..d06bcbc  master -> master
```

這時貢獻者的任務完成，於是主控者應該審核該分支，以下是主控者的兩種可能操作：

1. 主控者直接接受 (或拒絕)，如《初體驗》裏所示的那樣。
2. 主控者先測試，然後再決定是否要接受或拒絕。

我們這裡示範第 2 種。




<!--

### 貢獻者 : 將該專案 clone 到本地

```
PS D:\ccc\course\se108a> git clone https://github.com/ccccourse/mylodash.git
Cloning into 'mylodash'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), done.
```

### 貢獻者 : 創建一個新分支 add_chunk 並撰寫第一個函數

```
PS D:\ccc\course\se108a\mylodash> git checkout -b add_chunk
Switched to a new branch 'add_chunk'
```

現在我們已經在 add_chunk 這個分支中，此時我們應該開始寫 chunk 函數以及其測試程式！

(但是您可以將你之前寫好的第一個函數放入，這樣比較快，我們現在只練習 git 合作，不用再重寫程式了)

寫好之後請使用 mocha 進行測試！

```
PS D:\ccc\course\se108a\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]


  3 passing (34ms)
```

測試成功之後，請用下列指令推回到 github 。


```
PS D:\ccc\course\se108a\mylodash> git add -A
PS D:\ccc\course\se108a\mylodash> git commit -m "chunk test pass!"
[add_chunk db8edd4] chunk test pass!
 3 files changed, 26 insertions(+)
 create mode 100644 src/chunk.js
 create mode 100644 src/index.js
 create mode 100644 test/chunkTest.js

PS D:\ccc\course\se108a\mylodash> git push origin add_chunk
fatal: HttpRequestException encountered.
   傳送要求時發生錯誤。
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Counting objects: 7, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (5/5), done.
Writing objects: 100% (7/7), 824 bytes | 82.00 KiB/s, done.
Total 7 (delta 0), reused 0 (delta 0)
remote:
remote: Create a pull request for 'add_chunk' on GitHub by visiting:
remote:      https://github.com/ccccourse/mylodash/pull/new/add_chunk
remote:
To https://github.com/ccccourse/mylodash.git
 * [new branch]      add_chunk -> add_chunk
```

完成後你會看到 github 上的 mylodash 專案， master 仍然只有 README.md，但是沒有程式！

不過若看 branch add_chunk ，會發現有程式了。

## 專案主 : 檢視並測試該 branch 是否合格，若合格則接受



```
PS D:\ccc\course\se108a\owner\mylodash> git pull origin 

PS D:\ccc\course\se108a\owner\mylodash> mocha
Warning: Could not find any test files matching pattern: test
No test files found
PS D:\ccc\course\se108a\owner\mylodash> git checkout add_chunk
Switched to a new branch 'add_chunk'
Branch 'add_chunk' set up to track remote branch 'add_chunk' from 'origin'.
PS D:\ccc\course\se108a\owner\mylodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]


  3 passing (37ms)
```
-->