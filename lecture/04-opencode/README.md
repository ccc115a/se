### opencode

* https://opencode.school/

* [ai對話：opencode 實踐 loop engineering](https://gemini.google.com/app/fee77b67e36e8b27)
* https://github.com/agnusdei1207/opencode-orchestrator (用 opencode 做 harness 的插件)

`agnusdei1207/opencode-orchestrator` 是一個專為 OpenCode 開發的**多 Agent 協調插件（Multi-Agent Orchestrator Plugin）**。它正是為了解決複雜專案開發中的 **「Loop Engineering (任務循環與自動驗證)」** 以及 **「多 Agent 協同分工」** 需求而設計的套件。

---

### 核心運作機制與架構

該插件透過引入 **Mission Control（任務控制台）** 與 **Autonomous Mission Loop（自主任務循環）** 概念，將一個複雜的開發任務拆分給不同的專屬 AI 角色處理，並在背景形成自動驗證與修復的迴圈：

1. **4 種角色分工（Agent Council）**：
* 🎯 **Commander（指揮官）**：分析目標、劃分任務、調度 Agent。
* 🗺️ **Planner（規劃師）**：將大需求拆解為檔案層級的細部 TODO List 與執行策略。
* 🛠️ **Worker（執行者）**：負責具體的程式碼撰寫與 TDD（測試驅動開發）。
* 🛡️ **Reviewer（審核員/Gatekeeper）**：**Loop 的核心關卡**，負責執行測試與 Build 驗證。只有測試通過時才允許任務結束；若失敗則要求 Worker 重新修復。


2. **自帶記憶體與工具（Ebbinghaus Memory & Rust Tooling）**：
* **本地記憶機制**：結合 BM25、標籤與圖譜（Graph），紀錄長任務中的變數與上下文，避免長 Task 導致 AI 上下文遺忘。
* **高性能底層**：使用 Rust 實現 high-performance AST 解析與程式碼搜尋。



---

### 如何安裝與使用？

#### 1. 安裝套件

透過 npm 全局安裝，它會自動註冊到 OpenCode 的配置檔（`opencode.json` / `opencode.jsonc`）中：

```bash
npm install -g opencode-orchestrator

```

#### 2. 在 OpenCode 中啟用任務 Loop

安裝完成後，直接在 OpenCode 終端介面中輸入 `/task` 即可啟動 mission loop：

```text
/task "實作使用者註冊與驗證 API，並通過所有單元測試"

```

指令下達後，系統會在專案目錄下的 `.opencode/` 建立任務 Ledger，Commander → Planner → Worker → Reviewer 會自動啟動迴圈：

1. **Planner** 規劃檔案修改計畫。
2. **Worker** 撰寫程式碼。
3. **Reviewer** 執行測試（如 `npm test` 或 `pytest`）。
4. 若測試沒通過，Reviewer 將退回給 Worker 重寫（進入自主循環）。
5. 成功通過後，自動關閉任務並回報成果。

可用快捷控制指令：

* `/task <需求>`：啟動多 Agent 循環任務。
* `/stop` 或 `/cancel`：停止目前的任務迴圈。
* `Esc`：中斷或暫停迴圈。

---

### 總結

比起手寫 Bash 腳本，`opencode-orchestrator` 是目前 OpenCode 社群中成熟度極高且開箱即用的 Loop Engineering 方案。如果專案龐大、需求複雜、或是單一 Prompt 容易因為模型 Context Window 爆掉而失控，引入這個套件能大幅提升改 Code 的成功率。