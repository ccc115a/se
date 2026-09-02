
https://bojieli.github.io/ai-agent-book/book/chapter10/#loop-%E5%B7%A5%E7%A8%8B

https://huangruiteng.github.io/loopx/

把会干活的 Agent，接成可管理、可复盘、可持续改进的数字员工。

LoopX 决策 → Agent 执行 → 独立验证器证明 → LoopX 提交

其中，Agent 仍负责推理、调用工具和生成候选成果；LoopX 不替代 Agent 运行时，而是管理跨轮次的连续性。只有通过独立验证的结果才能写入持久进度并消耗配额；验证失败会进入修复或重规划，人工门禁、等待状态和预算上限则在执行前阻止循环继续。这个边界把 Loop 工程的原则变成了可检查的系统不变量：模型可以提出 “完成”，但不能批准自己的 “完成”。 LoopX v0.4.0 的受控 Turn 路径仍标为实验性，因此这里把它作为 “循环 + 验证 + 终止条件” 的具体框架，而不是一般任务质量提升的证据

