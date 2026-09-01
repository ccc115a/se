# git 與 github 使用

## 兩人合作 (一人分飾兩角)

貢獻者 fork 後加入新函數

```
PS D:\course\ccckmit\ccclodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ] (79ms)
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  compact
    √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]

  flattenDeep
    √ flattenDeep([1, [2, [3, [4]], 5]]) => [1, 2, 3, 4, 5]


  7 passing (157ms)

PS D:\course\ccckmit\ccclodash> git add -A
warning: LF will be replaced by CRLF in package-lock.json.
The file will have its original line endings in your working directory.
warning: LF will be replaced by CRLF in package.json.
The file will have its original line endings in your working directory.
PS D:\course\ccckmit\ccclodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  compact
    √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]

  flattenDeep
    √ flattenDeep([1, [2, [3, [4]], 5]]) => [1, 2, 3, 4, 5]


  7 passing (60ms)

PS D:\course\ccckmit\ccclodash> git add -A
PS D:\course\ccckmit\ccclodash> git commit -m "finished flattenDeep()"
husky > pre-commit (node v10.11.0)
25lRunning tasks for lib/*.js [started]
prettier --write [started]
prettier --write [completed]
git add [started]
git add [completed]
Running tasks for lib/*.js [completed]
25h25h[master ecd8601] finished flattenDeep()
 3 files changed, 41 insertions(+), 1 deletion(-)
 create mode 100644 lib/flattenDeep.js
 create mode 100644 test/flattenTest.js
PS D:\course\ccckmit\ccclodash> git push origin master
fatal: HttpRequestException encountered.
   傳送要求時發生錯誤。
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Counting objects: 9, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (9/9), done.
Writing objects: 100% (9/9), 1.91 KiB | 391.00 KiB/s, done.
Total 9 (delta 4), reused 0 (delta 0)
remote: Resolving deltas: 100% (4/4), completed with 4 local objects.
To https://github.com/ccckmit/ccclodash.git
   46a67a5..ecd8601  master -> master
```

## 主導者測試並納入專案

```
PS D:\course\se107a\example> git clone https://github.com/se107a/ccclodash.git
Cloning into 'ccclodash'...
remote: Enumerating objects: 129, done.
remote: Counting objects: 100% (129/129), done.
remote: Compressing objects: 100% (82/82), done.
remote: Total 129 (delta 56), reused 113 (delta 42), pack-reused 0
Receiving objects: 100% (129/129), 83.81 KiB | 350.00 KiB/s, done.
Resolving deltas: 100% (56/56), done.
PS D:\course\se107a\example> cd .\ccclodash\
PS D:\course\se107a\example\ccclodash> npm i
npm WARN npm npm does not support Node.js v10.11.0
npm WARN npm You should probably upgrade to a newer version of node as we
npm WARN npm can't make any promises that npm will work with this version.
npm WARN npm Supported releases of Node.js are the latest release of 4, 6, 7, 8, 9.
npm WARN npm You can find the latest version at https://nodejs.org/
added 349 packages in 37.461s
PS D:\course\se107a\example\ccclodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  compact
    √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  6 passing (78ms)

PS D:\course\se107a\example\ccclodash> git remote add ccckmit https://github.com/ccckmit/ccclodash.git
PS D:\course\se107a\example\ccclodash> git fetch ccckmit
remote: Enumerating objects: 21, done.
remote: Counting objects: 100% (21/21), done.
remote: Compressing objects: 100% (7/7), done.
remote: Total 14 (delta 8), reused 13 (delta 7), pack-reused 0
Unpacking objects: 100% (14/14), done.
From https://github.com/ccckmit/ccclodash
 * [new branch]      master     -> ccckmit/master
PS D:\course\se107a\example\ccclodash> git checkout -b ccckmitFlattenDeep
Switched to a new branch 'ccckmitFlattenDeep'
M       package-lock.json
M       package.json
PS D:\course\se107a\example\ccclodash> git merge ccckmit/master
error: Your local changes to the following files would be overwritten by merge:
        package-lock.json
        package.json
Please commit your changes or stash them before you merge.
Aborting
Updating f72805d..ecd8601
PS D:\course\se107a\example\ccclodash> git status
On branch ccckmitFlattenDeep
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

        modified:   package-lock.json
        modified:   package.json

no changes added to commit (use "git add" and/or "git commit -a")
PS D:\course\se107a\example\ccclodash> git stash
warning: LF will be replaced by CRLF in package-lock.json.
The file will have its original line endings in your working directory.
warning: LF will be replaced by CRLF in package.json.
The file will have its original line endings in your working directory.
Saved working directory and index state WIP on ccckmitFlattenDeep: f72805d Merge pull request #1 from ccckmit/master
PS D:\course\se107a\example\ccclodash> git merge ccckmit/master
Updating f72805d..ecd8601
Fast-forward
 index.js            |    3 +-
 lib/chunk.js        |   12 +-
 lib/flattenDeep.js  |   30 +
 package-lock.json   | 2111 +++++++++++++++++++++++++++++++++++++++++++++++++--
 package.json        |   25 +-
 test/flattenTest.js |    9 +
 6 files changed, 2110 insertions(+), 80 deletions(-)
 create mode 100644 lib/flattenDeep.js
 create mode 100644 test/flattenTest.js
PS D:\course\se107a\example\ccclodash> mocha


  chunk
    √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
    √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  compact
    √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  concat
    √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
    √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]

  flattenDeep
    √ flattenDeep([1, [2, [3, [4]], 5]]) => [1, 2, 3, 4, 5]


  7 passing (61ms)

PS D:\course\se107a\example\ccclodash> git checkout master
Switched to branch 'master'
Your branch is up to date with 'origin/master'.
PS D:\course\se107a\example\ccclodash> git merge ccckmit/master
Updating f72805d..ecd8601
Fast-forward
 index.js            |    3 +-
 lib/chunk.js        |   12 +-
 lib/flattenDeep.js  |   30 +
 package-lock.json   | 2111 +++++++++++++++++++++++++++++++++++++++++++++++++--
 package.json        |   25 +-
 test/flattenTest.js |    9 +
 6 files changed, 2110 insertions(+), 80 deletions(-)
 create mode 100644 lib/flattenDeep.js
 create mode 100644 test/flattenTest.js
PS D:\course\se107a\example\ccclodash> git diff origin/master
diff --git a/index.js b/index.js
index bcf6688..0c1845f 100644
--- a/index.js
+++ b/index.js
@@ -2,5 +2,6 @@
 module.exports = {
   chunk: require('./lib/chunk'),
   compact: require('./lib/compact'),
-  concat: require('./lib/concat')
+  concat: require('./lib/concat'),
+  flattenDeep: require('./lib/flattenDeep')
 }
...
PS D:\course\se107a\example\ccclodash> git push origin master
Username for 'https://github.com': ccckmit
Password for 'https://ccckmit@github.com':
Counting objects: 14, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (14/14), done.
Writing objects: 100% (14/14), 17.99 KiB | 1.20 MiB/s, done.
Total 14 (delta 8), reused 0 (delta 0)
remote: Resolving deltas: 100% (8/8), completed with 6 local objects.
To https://github.com/se107a/ccclodash.git
   f72805d..ecd8601  master -> master
```