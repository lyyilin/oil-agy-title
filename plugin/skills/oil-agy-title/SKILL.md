---
name: oil-agy-title
description: 管理 oil-agy-title 插件的 Antigravity 桌面端会话自动命名：检查运行状态与 Hook、预览或应用会话标题、固定/解锁标题、暂停/恢复自动命名、查看模型用量与切换廉价模型。当用户要求管理 Antigravity 桌面端会话标题或配置本插件时使用；不用于文章标题、文件重命名，也不在普通对话结束时由主 Agent 主动调用。
---

# oil-agy-title

管理 Antigravity 桌面端后台自动命名流程。自动命名由插件自带的 `Stop` Hook 在后台静默执行；主对话仅响应用户明确提出的检查、预览、固定、暂停或换模型请求。

## 脚本入口

主程序位于插件根目录的 `scripts/oil_agy_title.py`（即 `~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py`）。
默认会话 ID 自动读取环境变量 `$ANTIGRAVITY_CONVERSATION_ID`，也可显式传入 UUID。

## 常用命令

- 检查环境、RPC 与当前会话读取：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py doctor`
- 查看配置、已跟踪会话数和最近 5 条后台命名日志：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py status`
- 查看独立模型调用用量统计：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py usage`
- 预览当前会话新标题（不写入）：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py rename`
- 立即重命名当前会话并写回：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py rename --apply`
- 固定 / 解锁当前会话标题：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py lock`
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py unlock`
- 暂停 / 恢复全局自动命名：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py pause`
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py resume`
- 切换模型（默认 `agy` + `gemini-3.8-flash-low`）：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py configure --provider agy --model gpt-oss-120b-medium`
- 切换外部廉价 OpenAI 兼容 API（仅传环境变量名，不保存明文密钥）：
  `python3 ~/.gemini/config/plugins/oil-agy-title/scripts/oil_agy_title.py configure --provider openai_compatible --api-base-url https://... --api-key-env MY_API_KEY --model <model-id>`

## 返回状态说明

- `renamed`：新标题已写回并通过读回校验。`write_backend=conversation_service` 表示通过官方本地服务热更新（侧边栏即时刷新）；`write_backend=pbtxt_fallback` 表示降级写入 `annotations/<id>.pbtxt`（重载/重启后同步）。
- `kept` / `unchanged`：当前标题准确或对话无实质变化，保持原样。
- `locked` / `manual_title`：标题受保护（手工改名后自动锁定）；仅在用户明确要求恢复自动命名时执行 `unlock` 后再试。
- `stale_result`：模型生成期间对话或标题已变化，自动丢弃旧结果。
- `ambiguous_title`：与同项目已有会话重名且重试后仍无法区分，保留原名。
