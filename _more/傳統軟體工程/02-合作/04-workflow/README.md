# GithubFlow

* [阮一峰: Git 工作流程](http://www.ruanyifeng.com/blog/2015/12/git-workflow.html)
* [GitHub Flow 及 Git Flow 流程使用時機](https://blog.wu-boy.com/2017/12/github-flow-vs-git-flow/comment-page-1/)
* [git flow 實戰經驗談 part1 - 別再讓 gitflow 拖累團隊的開發速度](https://blog.hellojcc.tw/2017/12/14/the-flaw-of-git-flow/)

## Github Flow

第一步：根据需求，从master拉出新分支，不区分功能分支或补丁分支。

第二步：新分支开发完成后，或者需要讨论的时候，就向master发起一个pull request（简称PR）。

第三步：Pull Request既是一个通知，让别人注意到你的请求，又是一种对话机制，大家一起评审和讨论你的代码。对话过程中，你还可以不断提交代码。

第四步：你的Pull Request被接受，合并进master，重新部署后，原来你拉出来的那个分支就被删除。（先部署再合并也可。）

## GitFlow

長期分支

1. 主分支master
2. 开发分支develop

短期分支

1. 功能分支（feature branch）
2. 补丁分支（hotfix branch）
3. 预发分支（release branch）
