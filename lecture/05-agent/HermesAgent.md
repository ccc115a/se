* [AI 多 Agent + Loop Engineering](https://gemini.google.com/app/fee77b67e36e8b27)

* https://bojieli.github.io/ai-agent-book/book/chapter9/#%E7%9D%A1%E7%9C%A0%E5%AD%A6%E4%B9%A0%E6%95%B4%E5%90%88%E9%81%97%E5%BF%98%E4%B8%8E%E8%83%BD%E5%8A%9B%E4%BF%9D%E9%B2%9C


Hermes 则是一个更完整的后台记忆进化案例。它把长期信息分成有界的 MEMORY.md 与 USER.md、基于 SQLite/FTS5 的历史会话检索、按需加载的 Skill，以及 Honcho 等可选外部记忆提供者。历史检索返回原始消息而非先由 LLM 摘要，避免把检索和生成混成一个不可审计步骤。当一次任务包含较多工具调用、从错误或死路中恢复、收到用户纠正，或发现非显而易见的工作流时，后台复盘可以创建或局部修订 Skill；记忆和 Skill 写入还可以经过审批门控。独立的 Curator 进一步跟踪 Skill 的使用、陈旧和归档状态，在空闲期执行确定性修剪，并可选择运行 LLM 合并；变更前保存快照，错误整理可以回滚