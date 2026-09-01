* https://www.threads.com/@tysys1955/post/DWonXw1Ew1W?hl=en
* https://github.com/HKUDS/OpenHarness

tysys1955 16h

什麼是 Agent Harness？
就是包在 LLM 外面，讓它真正能幹活的基礎設施。
公式：Harness = 工具 + 知識 + 觀察 + 行動 + 權限
模型提供智力，Harness 提供手腳、眼睛、記憶和安全邊界。
核心是一個無限迴圈：
送 prompt → 模型決定用什麼工具 → 權限檢查 → Hook 攔截 → 執行 → 結
果回傳 → 模型再決定下一步。
模型決定「做什麼」，Harness 負責「怎麼做」。 

* https://www.threads.com/@0xbird/post/DWnjVP1GN_a?hl=en

Claude Code 的源码被人拆成了一份 21 页的架构分析报告，值得每个开发者仔细阅读10遍！

Reply

那 9 個 continue 點的設計很值得拿出來講——tool 執行完、需確認、等 user 回覆、compact 觸發、rate limit 處理…每一種「再跑一次」的理由都有自己的前處理邏輯，不是用 if-else 堆起來，而是分散在 9 個明確的 state transition 上。這種架構讓 /rewind 和 /compact 可以乾淨地掛上去，不用動到主循環本體。