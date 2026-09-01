# 简历描述参考（可直接改写后粘贴）

## 项目名称

智能资讯问答 Agent（FastAPI + LangGraph）

## 一句话

基于 FastAPI 与 LangGraph 的多会话 AI Agent 后端，支持 JWT 鉴权、Tool Calling 联网搜索与会话级状态持久化。

## Bullet 建议

- 实现注册 / 登录 / 创建会话 / 聊天等 REST 接口，鉴权层与聊天接入层分离，会话上下文通过依赖注入传入 Agent
- 使用 LangGraph 构建 chat ⇄ tool_call 两节点工作流：LLM 节点决策是否调用工具，工具节点异步执行并回写 State
- 设计用户 JWT 与会话 JWT 双层鉴权，结合 PostgreSQL Checkpointer 与 thread_id 实现多轮对话隔离与中断恢复（interrupt / resume）
- 对接 DeepSeek OpenAI 兼容 API，定制行业资讯 Prompt（时效问题强制搜索、拒绝编造），补充 Windows 本地启动与文档说明

## GitHub

推送后把仓库链接补在简历项目标题旁。
