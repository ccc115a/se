實務上 OpenCode 沒有內建的 worktree 旗標,但它天生跟 git worktree 搭配得很好,因為它是純粹讀取目前所在目錄的專案與分支。以下是完整流程:

## 基本流程(單一分支,不用 worktree)

```bash
# 安裝(如果還沒裝)
curl -fsSL https://opencode.ai/install | sh

# 進到專案目錄,初始化
cd your-project
opencode
/init   # 分析 repo,產生 AGENTS.md 記錄專案慣例
```

進去之後用 `Tab` 切換 **plan 模式**(唯讀,先討論怎麼改)和 **build 模式**(有寫入權限,實際動手改)。改完自己看 `git diff` 確認,再手動 commit——這個階段適合單純小改動或探索性工作。

## 用 git worktree 做平行開發(推薦用於正式功能開發)

因為 OpenCode 只看「目前所在目錄的分支」,每個 worktree 等於一個完全隔離的工作區,互不干擾:

```bash
# 從主 repo 建一個新的 worktree + 分支
git worktree add ../project-feat-search -b feat/search

# 進去,啟動獨立的 OpenCode session
cd ../project-feat-search
opencode
```

這樣你可以同時開好幾個終端機視窗,各自跑不同功能的 session,AI 改的東西只會落在對應的 worktree 目錄,主要工作目錄(main checkout)保持乾淨。搭配 tmux 更方便管理:

```bash
tmux new-window -n "feat-search" -c ../project-feat-search "opencode"
```

## 想要自動化整個生命週期

手動建 worktree、開終端機、cd、啟動這幾步有點瑣碎,社群有幾個外掛把它接成一條龍:

- **opencode-worktree(kdco)**:AI 自己呼叫 `worktree_create` 就會自動生出隔離的 worktree、開終端機、啟動 OpenCode;工作完呼叫 `worktree_delete` 會自動生成 commit message、commit、清掉 worktree。
- **opencode-worktree-session**:每個 AI session 自動建一個 worktree,session 結束時自動生成 commit message、push 分支、砍掉 worktree,而且會拒絕直接在 main 分支上跑,避免誤傷。

## Review 與收尾

不管手動還是自動化,合併前建議固定流程:

1. 在 worktree 裡跑 lint/test(`npm run check`、`npm run lint` 之類)
2. `git push` 該分支
3. 開 PR,走正常 code review
4. 合併後 `git worktree remove` 清掉工作目錄、刪掉分支

## 什麼時候該用哪種

- **單一小改動、探索性任務** → 直接在主目錄跑 OpenCode 就好,不用 worktree
- **正式功能開發、需要跟其他工作並行** → 手動 git worktree,乾淨又直覺
- **常態性地開很多平行 session、想省掉重複的建立/清理步驟** → 裝一個自動化 worktree 外掛