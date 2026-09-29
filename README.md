# 智能资讯问答 Agent

基于 FastAPI + LangGraph 的多会话 AI Agent 后端。支持 JWT 鉴权、工具调用（联网搜索 / 人机确认）、会话级 Checkpoint 持久化与流式输出。

> 在开源生产模板 [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template) 基础上二次开发：接入 DeepSeek、定制行业资讯助手 Prompt，并梳理鉴权 → 聊天 → Graph 全链路。

---

## 功能概览

| 能力 | 说明 |
|------|------|
| REST 聊天 API | `/chat` 整包返回、`/chat/stream` SSE 流式 |
| 双层 JWT | 用户 Token（注册/登录）→ 会话 Token（聊天） |
| LangGraph Agent | `chat` ⇄ `tool_call` 两节点，Command 路由 |
| Tool Calling | DuckDuckGo 搜索 + 网页正文抓取 + Human-in-the-loop（`ask_human`） |
| 网页抓取 | `fetch_webpage` 抓原文，弥补搜索摘要信息不足 |
| 会话持久化 | PostgreSQL Checkpointer + `thread_id` |
| 中断恢复 | `interrupt` / `resume`（人机确认后续跑） |

---

## 技术栈

- **Python 3.13+** · FastAPI · Uvicorn  
- **LangGraph** · LangChain · ChatOpenAI（OpenAI 兼容，默认 DeepSeek）  
- **PostgreSQL** · SQLModel · Alembic  
- **JWT**（python-jose）· Pydantic Settings  
- Docker Compose（本地数据库）

---

## 架构（请求怎么走）

```text
客户端
  │  POST /api/v1/auth/register | login     → 用户 JWT
  │  POST /api/v1/auth/session              → 会话 JWT
  │  POST /api/v1/chatbot/chat              → 聊天
  ▼
auth 层          chatbot 层              Agent 层
验 JWT / 开会话  →  收 messages         →  get_response
Depends 注入 Session                     ainvoke Graph
                                         ┌─ _chat（调 LLM，可选工具）
                                         └─ _tool_call（执行工具）→ 回 _chat
                                         END → ChatResponse
```

核心代码位置：

| 模块 | 路径 |
|------|------|
| 鉴权接口 | `app/api/v1/auth.py` |
| 聊天接口 | `app/api/v1/chatbot.py` |
| Graph / Agent | `app/core/langgraph/graph.py` |
| 工具注册 | `app/core/langgraph/tools/` |
| 系统提示词 | `app/core/prompts/system.md` |
| 模型注册 | `app/services/llm/registry.py` |

---

## 快速开始

### 1. 环境准备

- Python 3.13+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)（用于 PostgreSQL）
- DeepSeek API Key（[platform.deepseek.com](https://platform.deepseek.com/)）

### 2. 配置环境变量

```powershell
copy .env.example .env.development
```

编辑 `.env.development`，至少填写：

```env
OPENAI_API_KEY=你的_DeepSeek_Key
OPENAI_BASE_URL=https://api.deepseek.com/v1
DEFAULT_LLM_MODEL=deepseek-chat
JWT_SECRET_KEY=请换成足够长的随机字符串
```

**不要把真实 Key 提交到 Git。** `.env.development` 已在 `.gitignore` 中。

### 3. 启动（Windows）

```powershell
.\start-windows.ps1
```

或手动：

```powershell
docker compose up -d db
uv sync
$env:APP_ENV="development"
uv run uvicorn app.main:app --reload --port 8000
```

### 4. 调用 API

打开 Swagger：http://localhost:8000/docs

推荐顺序：

1. `POST /api/v1/auth/register` → 拿到用户 Token  
2. `POST /api/v1/auth/session`（Header 带用户 Token）→ 拿到会话 Token  
3. `POST /api/v1/chatbot/chat`（Header 带会话 Token）→ 开始提问  

示例 Body：

```json
{
  "messages": [
    { "role": "user", "content": "今天 AI 行业有什么重要新闻？" }
  ]
}
```

---

## 本仓库相对模板的主要改动

1. **LLM**：默认 DeepSeek（`deepseek-chat` / `deepseek-reasoner`），通过 `OPENAI_BASE_URL` 走兼容接口  
2. **Agent 人设**：`system.md` 改为行业资讯助手（时效问题强制搜索、中文优先、拒编造）  
3. **网页抓取工具**：新增 `fetch_webpage`（httpx 抓取 + 无依赖 HTML 转文本），形成「搜索 → 抓原文 → 综合回答」链路  
4. **工程脚本**：补充 Windows 启动脚本 `start-windows.ps1`  
5. **文档**：按「鉴权 → 聊天 → Graph」重写 README，便于复现与面试讲解  

---

## 自测问题（可选）

见 `evals/my_questions.txt`，覆盖：直接回答 / 需搜索 / 拒编造。

---

## 致谢

上游模板：[wassim249/fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)

---

## License

与上游模板保持一致，见 `LICENSE`。
