# oil-agy-title

Antigravity 桌面端话题自动命名插件（参考 `oil-oil/oil-codex-title` 规则移植）。

## 工作原理

1. **Stop Hook 异步派发**：每轮对话结束时触发 `Stop` Hook，立即在后台派生脱离会话的 worker 子进程并返回 `{}`，不阻塞界面。
2. **读取对话摘录**：直接读取 Antigravity 提供的 `transcript.jsonl`，仅提取最近 5 轮用户需求与最终回复，忽略工具日志与系统包装。
3. **轻量独立模型判断**：默认通过 `agy -p --model gemini-3.8-flash-low` 调用低成本结构化输出（复用现有 Antigravity 登录，零额外配置）；也支持切换到任意 OpenAI 兼容 API（如 Flash-Lite / DeepSeek / ZenMux）。
4. **热更新标题**：优先通过 Antigravity 官方本地 `ConversationService/UpdateConversation` 接口实时更新侧边栏、标题栏、SQLite 与全文检索索引；若在外部终端运行（无本地服务环境变量），自动降级为原子更新 `~/.gemini/antigravity/annotations/<id>.pbtxt`。

## 常用操作

直接对 Agent 说：
- 「检查 oil-agy-title 状态 / 跑一下 doctor」
- 「预览当前对话的新标题」 / 「给当前对话重新命名」
- 「固定当前对话标题」 / 「解锁当前对话标题」
- 「暂停自动命名」 / 「恢复自动命名」
- 「查看自动命名用量」
- 「把命名模型换成 gpt-oss-120b-medium」或配置自定义 OpenAI 兼容接口
