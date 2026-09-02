* https://bojieli.github.io/ai-agent-book/book/chapter10/#loop-%E5%B7%A5%E7%A8%8B

具体框架：LongHorizon-Harness。 LongHorizon-Harness 与 LoopX 都是 Loop 工程的具体实现，但关注的方向不同。LoopX 面向长期 Agent 工作的持久控制面；LongHorizon-Harness 则从多模态 Computer Use 出发，处理同一任务跨越 GUI、CLI、多个桌面应用和多次上下文刷新的连续执行问题。

LongHorizon-Harness 将长程执行重新表述为任务状态管理，并把自己的循环实现为 Manage–Execute–Audit（MEA）：Manager 根据原始目标、已核实进展、失败证据和剩余工作生成下一项有界子任务；Executor 在全新上下文中通过 GUI 或 CLI 改变环境；Auditor 再以只读方式检查真实结果。只有审计通过的内容才能进入下一轮任务状态，失败则被保留为恢复和重规划的依据。它通过适配层复用 Claude Code、Codex CLI 等执行后端，而不改写后端内部的 Agent loop。