# AI Workflow Builder — 完整项目介绍文档

> 轻量版 AI Agent 编排平台（类 Dify / Coze）  
> 版本：0.1.0 | 文档更新：2026-07-02（含模型管理模块）

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [项目结构](#3-项目结构)
4. [数据库设计](#4-数据库设计)
5. [认证模块（登录 / 注册）](#5-认证模块登录--注册)
6. [聊天模块](#6-聊天模块)
7. [画布 / 工作流模块](#7-画布--工作流模块)
8. [知识库模块](#8-知识库模块)
9. [工具模块](#9-工具模块)
10. [模型管理模块](#10-模型管理模块)
11. [工作流执行与监控](#11-工作流执行与监控)
12. [全局基础设施](#12-全局基础设施)
13. [部署与运行](#13-部署与运行)

---

## 1. 项目概述

**AI Workflow Builder** 是一个前后端分离的全栈 Web 应用，用户可通过可视化拖拽画布编排 AI Agent 工作流，并结合大模型对话、知识库文档管理、工具调用与工作流执行监控，完成从「对话」到「自动化流程」的完整闭环。

### 核心能力一览

| 模块 | 能力 |
|------|------|
| 认证 | 用户注册、登录、JWT 鉴权、路由守卫 |
| 聊天 | 多轮对话、SSE 流式输出、Markdown 渲染、对话历史持久化 |
| 画布 | 6 类节点拖拽、连线、节点配置、工作流 CRUD、位置持久化 |
| 知识库 | 知识库 CRUD、PDF/TXT/MD 上传、文档管理、RAG 节点联动 |
| 工具 | 9 个内置工具 + 自定义工具、在线测试、Tool 节点联动 |
| 模型 | 多提供商模型配置、Base URL / API Key 管理、高级策略、连接测试、LLM 节点联动 |
| 执行 | 工作流一键运行、SSE 节点状态推送、执行日志、运行历史、模型配置追踪 |

### 页面导航

顶部 Tab 切换五个主页面：**聊天** | **画布** | **知识库** | **工具** | **模型**

---

## 2. 技术架构

### 2.1 技术栈总览

| 层级 | 技术选型 |
|------|----------|
| 前端框架 | Vue 3 + TypeScript |
| 构建工具 | Vite 6 |
| 状态管理 | Vuex 4 |
| 路由 | Vue Router 4 |
| UI 组件库 | Element Plus |
| 样式 | Tailwind CSS + 自定义 CSS |
| 画布引擎 | Vue Flow (@vue-flow/core) |
| HTTP | Axios |
| 流式通信 | SSE（Server-Sent Events） |
| Markdown | marked + highlight.js |
| 后端框架 | FastAPI |
| ORM | SQLAlchemy 2 |
| 数据库 | MySQL |
| 认证 | JWT（python-jose）+ bcrypt |
| 大模型 | 阿里云百炼 DashScope（OpenAI 兼容 API） |
| 文件上传 | python-multipart + 本地磁盘存储 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     浏览器 (Vue 3 SPA)                       │
│  Login/Register │ Chat │ Canvas │ Knowledge │ Tools │ Models   │
│       ↓              ↓       ↓         ↓          ↓       ↓     │
│   Vuex Store    Axios (+ JWT)    SSE (chat / workflow)        │
└──────────────────────────┬────────────────────────────────────┘
                           │ HTTP /api/*
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI 后端 (:8000)                       │
│  auth │ chat │ workflows │ knowledge │ tools │ models │ execution │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           MySQL      DashScope API   uploads/
```

### 2.3 API 基础信息

- **Base URL**：`http://localhost:8000/api`
- **前端代理**：Vite 将 `/api` 代理至 `http://localhost:8000`
- **认证方式**：`Authorization: Bearer <JWT_TOKEN>`
- **内容类型**：`application/json`（文件上传为 `multipart/form-data`）

---

## 3. 项目结构

```
Project/
├── Be_end/                          # 后端
│   ├── main.py                      # FastAPI 入口
│   ├── config.py                    # 配置（数据库、JWT、百炼 API）
│   ├── database.py                  # SQLAlchemy 引擎与会话
│   ├── models.py                    # ORM 模型
│   ├── schemas.py                   # Pydantic 请求/响应模型
│   ├── security.py                  # 密码哈希、JWT、鉴权依赖
│   ├── workflow_executor.py         # 工作流执行引擎
│   ├── model_runtime.py             # 模型配置解析与 LLM 运行时
│   ├── tool_handlers.py             # 工具执行 Handler
│   ├── schema.sql                   # 数据库建表脚本
│   ├── requirements.txt
│   ├── uploads/                     # 知识库文档存储目录
│   └── routes/
│       ├── auth.py
│       ├── chat.py
│       ├── workflow.py
│       ├── knowledge.py
│       ├── tools.py
│       ├── models.py
│       └── execution.py
│
├── Front_end/                       # 前端
│   ├── public/
│   │   └── login-bg.png             # 登录页背景图
│   ├── src/
│   │   ├── api/                     # API 封装
│   │   ├── assets/                  # 样式资源
│   │   ├── components/
│   │   │   ├── canvas/              # 画布相关组件
│   │   │   ├── chat/                # 聊天相关组件
│   │   │   ├── knowledge/           # 知识库组件
│   │   │   ├── tools/               # 工具组件
│   │   │   ├── models/              # 模型配置组件
│   │   │   ├── layout/              # 布局组件
│   │   │   └── common/              # 通用组件
│   │   ├── composables/             # 组合式函数
│   │   ├── router/                  # 路由配置
│   │   ├── store/                   # Vuex 模块
│   │   ├── types/                   # TypeScript 类型
│   │   ├── utils/                   # 工具函数
│   │   └── views/                   # 页面视图（含 ModelsView.vue）
│   ├── package.json
│   └── vite.config.ts
│
├── PROJECT_DOCUMENTATION.md         # 本文档
└── RESUME_PROJECT.txt               # 简历项目描述
```

---

## 4. 数据库设计

数据库名：`AiWork`（MySQL）

### 4.1 表结构

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `users` | 用户 | id, username, email, hashed_password |
| `conversations` | 对话 | id, user_id, title |
| `messages` | 消息 | id, conversation_id, role, content |
| `workflows` | 工作流 | id, user_id, name, graph_json, status |
| `knowledge_bases` | 知识库 | id, user_id, name, doc_count |
| `documents` | 文档 | id, kb_id, filename, file_path, status |
| `tools` | 工具 | id, name, handler_name, schema_json |
| `model_profiles` | 模型配置 | id, user_id, provider, base_url, api_key, model_id, config_json |
| `workflow_runs` | 工作流运行记录 | id, workflow_id, status, input_json, output_json, logs_json |

### 4.2 工作流 graph_json 结构

```json
{
  "nodes": [
    {
      "id": "node_1234567890",
      "type": "llm",
      "label": "LLM 推理",
      "position": { "x": 300, "y": 200 },
      "config": {
        "modelProfileId": 1,
        "modelProfileName": "模型1",
        "prompt": "请总结：{{input}}",
        "systemPrompt": "你是一个问答客服",
        "temperature": 0.7,
        "maxTokens": 2048
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1234567891",
      "source": "node_xxx",
      "target": "node_yyy",
      "sourceHandle": null,
      "targetHandle": null
    }
  ]
}
```

---

## 5. 认证模块（登录 / 注册）

### 5.1 功能说明

#### 登录页 (`/login`)

- 全屏背景图（沙丘水域风景）
- 毛玻璃风格登录卡片（backdrop-filter blur）
- 浮动标签输入框（Username / Password）
- Element Plus 图标（用户、锁）
- 表单校验：用户名、密码必填
- 「Forgot password?」提示（联系管理员）
- 「Create one.」跳转注册页
- 登录成功：JWT 存入 localStorage，跳转 `/chat`

#### 注册页 (`/register`)

- 与登录页统一视觉风格
- 字段：Username、Email、Password、Confirm Password
- 邮箱格式校验、两次密码一致性校验
- 注册成功提示后跳转登录页

#### 路由守卫

- 未登录访问受保护页面 → 跳转 `/login`
- 已登录访问 `/login` 或 `/register` → 跳转 `/chat`
- Token 持久化于 `localStorage`，刷新页面后自动调用 `/auth/me` 恢复用户信息

### 5.2 后端接口

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| `POST` | `/api/auth/register` | 否 | 用户注册 |
| `POST` | `/api/auth/login` | 否 | 用户登录，返回 JWT |
| `GET` | `/api/auth/me` | 是 | 获取当前用户信息 |

#### POST `/api/auth/register`

**请求体：**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**响应（201）：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-07-02T10:00:00"
}
```

**错误：**
- `400` Username already registered
- `400` Email already registered

#### POST `/api/auth/login`

**请求体：**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**错误：**
- `401` Incorrect username or password

#### GET `/api/auth/me`

**响应：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-07-02T10:00:00"
}
```

### 5.3 前端文件

| 文件 | 说明 |
|------|------|
| `views/LoginView.vue` | 登录页 |
| `views/RegisterView.vue` | 注册页 |
| `assets/auth.css` | 登录/注册共用样式 |
| `api/auth.ts` | 认证 API 封装 |
| `store/auth.ts` | 认证状态管理 |
| `router/index.ts` | 路由守卫 |
| `utils/request.ts` | Axios JWT 拦截器 |

---

## 6. 聊天模块

### 6.1 功能说明

#### 页面布局

- **左侧**：对话历史列表（ConversationList）
  - 「+ 新建对话」按钮
  - 对话标题列表，点击切换
  - 当前对话高亮
- **右侧**：聊天主区域
  - 消息列表（MessageList）：自动滚到底部
  - 单条消息（MessageItem）：区分用户/AI，AI 消息支持 Markdown 渲染与代码高亮
  - 输入框（ChatInput）：Enter 发送，Shift+Enter 换行

#### 核心特性

- **SSE 流式输出**：AI 回复逐字推送，打字机效果
- **多轮上下文**：后端取最近 20 条消息作为 LLM 上下文
- **自动标题**：首条用户消息自动设为对话标题（截取前 50 字）
- **持久化**：用户消息与 AI 回复均存入 MySQL

### 6.2 后端接口

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| `GET` | `/api/chat/conversations` | 是 | 获取对话列表 |
| `POST` | `/api/chat/conversations` | 是 | 创建新对话 |
| `GET` | `/api/chat/conversations/{conv_id}` | 是 | 获取对话详情（含消息） |
| `DELETE` | `/api/chat/conversations/{conv_id}` | 是 | 删除对话 |
| `POST` | `/api/chat/conversations/{conv_id}/messages` | 是 | 发送消息（SSE 流式） |

#### GET `/api/chat/conversations`

**响应：**
```json
[
  {
    "id": 1,
    "title": "介绍 FastAPI",
    "created_at": "2026-07-02T10:00:00",
    "updated_at": "2026-07-02T10:05:00"
  }
]
```

#### POST `/api/chat/conversations`

**请求体：**
```json
{ "title": "新对话" }
```

#### GET `/api/chat/conversations/{conv_id}`

**响应：**
```json
{
  "id": 1,
  "title": "介绍 FastAPI",
  "messages": [
    { "id": 1, "conversation_id": 1, "role": "user", "content": "介绍FastAPI", "created_at": "..." },
    { "id": 2, "conversation_id": 1, "role": "assistant", "content": "FastAPI是...", "created_at": "..." }
  ],
  "created_at": "...",
  "updated_at": "..."
}
```

#### POST `/api/chat/conversations/{conv_id}/messages`（SSE）

**请求体：**
```json
{ "content": "用户输入的消息" }
```

**响应类型：** `text/event-stream`

**SSE 事件格式：**

| type | 字段 | 说明 |
|------|------|------|
| `delta` | `content` | 增量文本片段 |
| `done` | `message_id`, `created_at` | 流结束，消息已持久化 |
| `error` | `content` | 错误信息 |

**示例流：**
```
data: {"type": "delta", "content": "Fast"}
data: {"type": "delta", "content": "API"}
data: {"type": "done", "message_id": 42, "created_at": "2026-07-02T10:05:00"}
```

### 6.3 前端文件

| 文件 | 说明 |
|------|------|
| `views/ChatView.vue` | 聊天页容器 |
| `components/chat/ConversationList.vue` | 对话列表 |
| `components/chat/MessageList.vue` | 消息滚动列表 |
| `components/chat/MessageItem.vue` | 单条消息 |
| `components/chat/ChatInput.vue` | 输入框 |
| `components/common/MarkdownRenderer.vue` | Markdown + 代码高亮 |
| `api/chat.ts` | 聊天 API |
| `store/chat.ts` | 聊天状态 + SSE 管理 |
| `utils/sse.ts` | SSE 连接工具 |

### 6.4 大模型配置

- **提供商**：阿里云百炼 DashScope
- **兼容协议**：OpenAI API 格式
- **默认模型**：`qwen3.7-plus`
- **配置项**：`DASHSCOPE_API_KEY`、`DASHSCOPE_BASE_URL`、`DASHSCOPE_MODEL`（`config.py`）

---

## 7. 画布 / 工作流模块

### 7.1 功能说明

#### 页面布局（三栏）

| 区域 | 组件 | 功能 |
|------|------|------|
| 左侧 | NodePalette | 节点面板，分类展示可拖拽节点 |
| 中间 | WorkflowCanvas | Vue Flow 画布，拖拽放置、连线、小地图 |
| 右侧 | NodeConfigPanel | 节点配置面板，动态表单 |
| 底部 | ExecutionLog | 执行日志（Phase 7） |

#### 顶部工具栏

- **工作流列表**：抽屉展示已保存工作流，支持加载、删除
- **工作流名称**：可编辑，实时同步 store
- **保存**：创建或更新工作流至数据库
- **新建**：清空画布，创建新工作流
- **运行**：触发工作流执行（需已保存 + 有起始节点）

#### 节点类型（6 类）

| 类型 | 标识 | 分类 | 说明 |
|------|------|------|------|
| 起始 | `start` | 流程控制 | 工作流入口，定义输入参数 |
| 输出 | `end` | 流程控制 | 工作流出口，格式化最终输出 |
| 条件判断 | `condition` | 流程控制 | if/else 分支，双输出 Handle |
| LLM 推理 | `llm` | AI 节点 | 调用大语言模型 |
| RAG 检索 | `rag` | AI 节点 | 从知识库检索（当前模拟） |
| 工具调用 | `tool` | 工具 | 调用内置/自定义工具 |

#### 画布交互

| 操作 | 实现 |
|------|------|
| 拖拽放置节点 | 从 NodePalette 拖入画布，`onDrop` + `screenToFlowCoordinate` |
| 节点连线 | 从 Handle 拖到另一节点，`@connect` 事件 |
| 删除连线 | 点击连线 → 右侧面板删除 / 按 Delete 键 |
| 节点配置 | 点击节点 → 右侧 NodeConfigPanel 动态表单 |
| 删除节点 | 节点悬停显示 × 按钮 |
| 节点位置持久化 | `node-drag-stop` 同步坐标至 store，`loadVersion` 强制重挂载 |
| 节点执行高亮 | 黄色=执行中，绿色=成功，红色=失败 |

#### 各节点配置项

**起始节点 (start)**
- 节点名称
- 输入参数定义（JSON）

**LLM 节点 (llm)**
- 节点名称
- **模型配置**：下拉选择「模型」页已保存的配置（留空则使用默认模型）
- System Prompt
- Prompt 模板（支持 `{{input}}` 引用上游输出；上游为 RAG 时自动注入检索片段）
- 温度（0-2，节点级，独立于模型页策略）
- 最大 Token（256-8192，节点级）

**RAG 节点 (rag)**
- 节点名称
- 知识库选择（下拉，来自知识库 API）
- 检索数量 Top K（1-20）
- 相似度阈值（0-1）

**Tool 节点 (tool)**
- 节点名称
- 工具选择（来自工具 API）
- HTTP 请求 URL（http_request 工具时）
- 参数 JSON

**Condition 节点 (condition)**
- 节点名称
- 条件表达式
- True/False 分支标签
- 双输出 Handle（左 30% / 右 70%）

**输出节点 (end)**
- 节点名称
- 输出格式：直接输出 / Markdown / JSON
- 输出模板（支持 `{{output}}`）

### 7.2 后端接口（工作流 CRUD）

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| `GET` | `/api/workflows` | 是 | 获取工作流列表 |
| `POST` | `/api/workflows` | 是 | 创建工作流 |
| `GET` | `/api/workflows/{wf_id}` | 是 | 获取工作流详情 |
| `PUT` | `/api/workflows/{wf_id}` | 是 | 更新工作流 |
| `DELETE` | `/api/workflows/{wf_id}` | 是 | 删除工作流 |

#### POST `/api/workflows`

**请求体：**
```json
{
  "name": "我的工作流",
  "description": "可选描述"
}
```

#### PUT `/api/workflows/{wf_id}`

**请求体：**
```json
{
  "name": "更新后的名称",
  "description": "描述",
  "graph_json": {
    "nodes": [...],
    "edges": [...]
  },
  "status": "draft"
}
```

#### GET `/api/workflows/{wf_id}`

**响应：**
```json
{
  "id": 1,
  "name": "工作流0702",
  "description": "",
  "graph_json": { "nodes": [...], "edges": [...] },
  "status": "draft",
  "created_at": "...",
  "updated_at": "..."
}
```

### 7.3 前端文件

| 文件 | 说明 |
|------|------|
| `views/CanvasView.vue` | 画布页容器 + 工具栏 |
| `components/canvas/WorkflowCanvas.vue` | Vue Flow 画布主组件 |
| `components/canvas/NodePalette.vue` | 节点拖拽面板 |
| `components/canvas/NodeConfigPanel.vue` | 节点配置面板 |
| `components/canvas/ExecutionLog.vue` | 执行日志面板 |
| `components/canvas/nodes/*.vue` | 6 类自定义节点组件 |
| `composables/useNodeExecStatus.ts` | 节点执行状态样式 |
| `api/workflow.ts` | 工作流 API |
| `store/canvas.ts` | 画布状态管理 |

---

## 8. 知识库模块

### 8.1 功能说明

#### 列表页

- 知识库卡片网格展示：名称、描述、文档数、创建时间
- 「新建知识库」按钮 → 弹出创建对话框（名称 + 描述）
- 每张卡片：**管理**（进入详情）、**删除**（二次确认）

#### 详情页（DocUpload）

- 顶部：返回列表、知识库名称、文档数
- **上传区域**：FileUploader 组件，支持拖拽上传 PDF/TXT/MD，显示上传进度
- **文档列表**：文件名、状态（处理中/就绪/失败）、上传时间、删除按钮

#### RAG 节点联动

- 画布 RAG 节点配置面板挂载时自动拉取知识库列表
- 下拉框显示真实知识库名称
- RAG 节点卡片显示已选知识库名

### 8.2 后端接口

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| `GET` | `/api/knowledge` | 是 | 获取知识库列表 |
| `POST` | `/api/knowledge` | 是 | 创建知识库 |
| `DELETE` | `/api/knowledge/{kb_id}` | 是 | 删除知识库（级联删文档和文件） |
| `GET` | `/api/knowledge/{kb_id}/documents` | 是 | 获取文档列表 |
| `POST` | `/api/knowledge/{kb_id}/upload` | 是 | 上传文档（multipart） |
| `DELETE` | `/api/knowledge/{kb_id}/documents/{doc_id}` | 是 | 删除文档 |

#### POST `/api/knowledge`

**请求体：**
```json
{
  "name": "技术文档库",
  "description": "存放 API 文档"
}
```

**响应：**
```json
{
  "id": 1,
  "name": "技术文档库",
  "description": "存放 API 文档",
  "docCount": 0,
  "createdAt": "2026-07-02T10:00:00"
}
```

#### POST `/api/knowledge/{kb_id}/upload`

**请求：** `multipart/form-data`，字段名 `file`

**支持格式：** `.pdf`、`.txt`、`.md`

**存储路径：** `uploads/{kb_id}/{filename}`

**响应：**
```json
{
  "id": 1,
  "filename": "api-doc.pdf",
  "chunkCount": 0,
  "status": "ready",
  "createdAt": "2026-07-02T10:00:00"
}
```

#### GET `/api/knowledge/{kb_id}/documents`

**响应：**
```json
[
  {
    "id": 1,
    "filename": "api-doc.pdf",
    "chunkCount": 0,
    "status": "ready",
    "createdAt": "2026-07-02T10:00:00"
  }
]
```

### 8.3 前端文件

| 文件 | 说明 |
|------|------|
| `views/KnowledgeView.vue` | 知识库页容器（列表 ↔ 详情切换） |
| `components/knowledge/KBList.vue` | 知识库卡片列表 |
| `components/knowledge/KBCreate.vue` | 创建对话框 |
| `components/knowledge/DocUpload.vue` | 详情页（上传 + 文档列表） |
| `components/common/FileUploader.vue` | 通用拖拽上传组件 |
| `api/knowledge.ts` | 知识库 API |
| `store/knowledge.ts` | 知识库状态管理 |

---

## 9. 工具模块

### 9.1 功能说明

#### 工具市场页

- 工具卡片网格，按分类筛选（全部 / 搜索 / 代码 / API / 文本 / 数据 / 实用 / 自定义）
- 每张卡片：名称、描述、分类标签、「查看详情」
- 自定义工具显示「删除」按钮
- 「添加自定义工具」：选择底层能力 + 命名 + 描述

#### 工具详情（抽屉）

- 工具描述、参数 JSON Schema
- **在线测试**：根据 Schema 动态生成表单，填写参数后「运行测试」
- 测试结果 JSON 展示，HTTP 412 等错误附带中文说明

#### Tool 节点联动

- 画布 Tool 节点配置面板从 API 拉取工具列表
- 下拉显示工具中文名
- 节点卡片显示已选工具名

### 9.2 内置工具（9 个）

| 名称 | handler | 分类 | 功能 |
|------|---------|------|------|
| web_search | web_search | search | 模拟互联网搜索 |
| code_exec | code_exec | code | Python 代码执行（子进程，15 秒超时） |
| http_request | http_request | api | HTTP GET/POST 请求 |
| json_parse | json_parse | data | JSON 解析验证 |
| text_split | text_split | text | 按分隔符拆分文本 |
| string_replace | string_replace | text | 字符串查找替换 |
| regex_match | regex_match | text | 正则表达式匹配 |
| text_length | text_length | text | 文本字符/行/词统计 |
| current_time | current_time | utility | 获取当前系统时间 |

### 9.3 自定义工具

- 用户可基于已有 handler 创建自定义工具（如封装专属 API）
- 工具标识名唯一，英文+下划线
- 内置工具不可删除

### 9.4 后端接口

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| `GET` | `/api/tools/handlers` | 是 | 获取可用 handler 列表 |
| `GET` | `/api/tools` | 是 | 获取工具列表（支持 `?category=` 筛选） |
| `POST` | `/api/tools` | 是 | 创建自定义工具 |
| `DELETE` | `/api/tools/{tool_id}` | 是 | 删除自定义工具 |
| `GET` | `/api/tools/{tool_id}` | 是 | 获取工具详情 |
| `POST` | `/api/tools/{tool_id}/test` | 是 | 在线测试工具 |

#### GET `/api/tools?category=search`

**响应：**
```json
[
  {
    "id": 1,
    "name": "web_search",
    "description": "搜索互联网获取信息",
    "category": "search",
    "schema": {
      "type": "object",
      "properties": {
        "query": { "type": "string", "description": "搜索关键词" }
      },
      "required": ["query"]
    }
  }
]
```

#### POST `/api/tools`

**请求体：**
```json
{
  "name": "my_api_tool",
  "description": "调用公司内部 API",
  "category": "custom",
  "handler_name": "http_request",
  "schema_json": null
}
```

#### POST `/api/tools/{tool_id}/test`

**请求体：**
```json
{
  "params": {
    "query": "FastAPI"
  }
}
```

**响应：**
```json
{
  "success": true,
  "result": {
    "query": "FastAPI",
    "results": [...]
  }
}
```

### 9.5 前端文件

| 文件 | 说明 |
|------|------|
| `views/ToolsView.vue` | 工具市场页容器 |
| `components/tools/ToolList.vue` | 工具卡片列表（分类筛选） |
| `components/tools/ToolDetail.vue` | 工具详情 + 在线测试 |
| `components/tools/ToolCreate.vue` | 创建自定义工具对话框 |
| `api/tools.ts` | 工具 API |
| `store/tools.ts` | 工具状态管理 |
| `utils/toolLabels.ts` | 工具显示名映射 |

---

## 10. 模型管理模块

### 10.1 功能说明

模型管理页对应画布中的 **LLM 推理** 节点，用于集中管理大模型连接信息与高级运行时策略。**前端模型页配置优先于后端 `config.py` 默认设置**。

#### 页面布局

- **顶部**：标题 + 「添加模型」按钮
- **说明区**：已实现的可配置项与暂未纳入项提示
- **卡片列表**：每张卡片展示配置名、提供商、模型 ID、脱敏 API Key、Agent 模式、历史策略
- **操作**：配置（编辑抽屉）、测试连接、删除
- **编辑抽屉**：分块表单（连接配置 / 上下文管理 / 历史对话 / Agent 行为 / 可观测性）

#### 模型类型（提供商预设）

| 类型 | 标识 | 默认 Base URL | 说明 |
|------|------|---------------|------|
| 通义千问 | `qianwen` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 阿里云百炼 OpenAI 兼容接口 |
| DeepSeek | `deepseek` | `https://api.deepseek.com/v1` | — |
| OpenAI GPT | `gpt` | `https://api.openai.com/v1` | — |
| Claude | `claude` | `https://api.anthropic.com/v1` | 需 OpenAI 兼容代理网关 |
| 自定义导入 | `custom` | 用户填写 | 自行填写 Base URL 与模型 ID |

#### 高级配置项（`config_json`）

**上下文管理**

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `maxContextTokens` | 最大上下文 Token | 8192 |
| `systemTokenRatio` | System 层预算比例 (%) | 10 |
| `userTokenRatio` | User 层预算比例 (%) | 60 |
| `toolTokenRatio` | Tool 层预算比例 (%) | 10 |
| `ragTokenRatio` | RAG 注入预算比例 (%) | 20 |
| `compressionStrategy` | 压缩策略：`none` / `truncate_oldest` / `summarize` | `none` |

**历史对话策略**

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `strategy` | `sliding_window` / `summarize` / `vector_retrieval` | `sliding_window` |
| `maxMessages` | 最大保留消息数 | 20 |
| `windowSize` | 滑动窗口大小 | 10 |

**Agent 行为**

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `mode` | `react` / `plan_execute` / `tool_calling` | `tool_calling` |
| `toolWhitelist` | 工具白名单（空=全部允许） | `[]` |
| `maxIterations` | 最大迭代次数 | 10 |

**可观测性**

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `enableTracing` | 启用步骤追踪（执行日志记录延迟等） | `true` |
| `logToolCalls` | 记录工具调用链 | `true` |

> **暂未纳入**：LoRA 端点切换、多模型按任务路由、状态图可视化（需独立 Agent 运行时引擎）。

#### LLM 节点联动

- 画布 LLM 节点配置面板下拉选择已保存的模型配置
- 留空则自动使用用户「默认模型」
- 节点卡片显示配置名（如 `配置: 模型1` 或 `默认 · 模型1`）
- 工作流执行时由 `model_runtime.py` 加载配置并调用对应 API

#### 配置验证方式

1. **测试连接**：`POST /api/models/{id}/test`，验证 URL / API Key / 模型 ID
2. **工作流运行**：执行日志出现 `模型配置生效: [配置名] 模型ID @ BaseURL | 延迟 Xms | Agent=... | 策略=...`
3. **RAG 联动**：上游接 RAG 节点时，日志显示 `RAG注入=N段`，且 `prompt` Token 明显增加
4. **多配置对比**：不同配置可设置不同 Agent 模式，日志中 `Agent=` 字段会不同

### 10.2 后端接口

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| `GET` | `/api/models` | 是 | 获取模型配置列表（API Key 脱敏） |
| `POST` | `/api/models` | 是 | 创建模型配置 |
| `GET` | `/api/models/{id}` | 是 | 获取详情（含完整 API Key） |
| `PUT` | `/api/models/{id}` | 是 | 更新模型配置 |
| `DELETE` | `/api/models/{id}` | 是 | 删除模型配置 |
| `POST` | `/api/models/{id}/test` | 是 | 测试连接 |

#### POST `/api/models`

**请求体：**
```json
{
  "name": "模型1",
  "provider": "qianwen",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "api_key": "sk-***",
  "model_id": "qwen3.7-plus",
  "is_default": true,
  "config_json": {
    "context": {
      "maxContextTokens": 8192,
      "systemTokenRatio": 10,
      "userTokenRatio": 60,
      "toolTokenRatio": 10,
      "ragTokenRatio": 20,
      "compressionStrategy": "none"
    },
    "history": {
      "strategy": "sliding_window",
      "maxMessages": 20,
      "windowSize": 10
    },
    "agent": {
      "mode": "plan_execute",
      "toolWhitelist": [],
      "maxIterations": 10
    },
    "observability": {
      "enableTracing": true,
      "logToolCalls": true
    }
  }
}
```

**响应（201）：** 含完整 `apiKey` 的详情对象。

#### GET `/api/models`

**响应：**
```json
[
  {
    "id": 1,
    "name": "模型1",
    "provider": "qianwen",
    "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "apiKeyMasked": "sk-6***1111",
    "modelId": "qwen3.7-plus",
    "config": { "...": "..." },
    "isDefault": true,
    "createdAt": "2026-07-02T10:00:00",
    "updatedAt": "2026-07-02T19:00:00"
  }
]
```

#### POST `/api/models/{id}/test`

**请求体：**
```json
{ "message": "你好，请回复 OK" }
```

**响应（成功）：**
```json
{
  "success": true,
  "reply": "OK",
  "model": "qwen3.7-plus",
  "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}
```

### 10.3 运行时对接（`model_runtime.py`）

工作流执行时 LLM 节点的配置加载优先级：

1. 节点 `config.modelProfileId` 指定配置
2. 用户 `is_default=true` 的默认配置
3. 回退至 `config.py` 服务端默认（`DASHSCOPE_*`）

运行时应用逻辑：

- 使用配置中的 `base_url`、`api_key`、`model_id` 创建 OpenAI 兼容客户端
- 按 Token 预算比例截断 System / User / RAG 内容
- 上游 RAG 节点输出的 `chunks` 自动注入 Prompt（`【检索上下文】` 前缀）
- 应用历史策略与压缩策略构建 messages
- 节点级 `temperature`、`maxTokens` 仍由画布节点配置控制
- 执行后生成 `trace` 对象，写入执行日志（配置名、延迟、Agent 模式、RAG 注入段数、Token 用量）

### 10.4 前端文件

| 文件 | 说明 |
|------|------|
| `views/ModelsView.vue` | 模型管理页容器 |
| `components/models/ModelList.vue` | 模型配置卡片列表 |
| `components/models/ModelEditor.vue` | 创建/编辑抽屉（分块高级配置） |
| `api/models.ts` | 模型 API 封装 |
| `store/models.ts` | 模型状态管理 |
| `types/models.ts` | 类型定义、提供商预设、默认配置 |

### 10.5 数据库表 `model_profiles`

```sql
CREATE TABLE model_profiles (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  provider VARCHAR(50) NOT NULL,
  base_url VARCHAR(500) NOT NULL,
  api_key VARCHAR(500) NOT NULL,
  model_id VARCHAR(100) NOT NULL,
  config_json JSON,
  is_default BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 11. 工作流执行与监控

### 11.1 功能说明

#### 运行流程

1. 用户点击「运行」→ 弹出输入对话框
2. 若有未保存更改，自动保存
3. 后端按拓扑顺序从「起始」节点开始依次执行
4. SSE 实时推送每个节点的开始/成功/失败状态
5. 前端节点高亮 + 底部日志面板实时更新
6. 执行完成后显示最终输出，记录存入 `workflow_runs` 表

#### 执行日志面板（ExecutionLog）

- 底部可折叠面板，默认高度 200px
- **顶部拖拽条**：调整面板高度（120px ~ 560px）
- **右侧分隔条**：调整「节点输出」区域宽度（200px ~ 720px）
- 布局尺寸记忆至 localStorage
- 日志按时间排列，点击可定位到对应节点
- 右侧显示选中节点输出或最终输出
- 「运行历史」按钮打开历史抽屉

#### 节点执行逻辑

| 节点类型 | 执行行为 |
|----------|----------|
| start | 透传用户输入 |
| llm | 加载用户模型配置（`model_runtime.py`），调用对应 API；支持 Prompt 模板、`{{input}}` 变量、RAG 片段注入；记录 trace 至执行日志 |
| rag | 模拟知识库检索（返回 chunks 列表） |
| tool | 调用 tool_handlers 对应 handler |
| condition | 评估条件表达式，返回 passed 布尔值 |
| end | 按模板格式化最终输出 |

#### 执行日志中的模型追踪

LLM 节点执行成功后，若 `enableTracing=true`，日志输出示例：

```
[info] 模型配置生效: [模型1] qwen3.7-plus @ https://dashscope.aliyuncs.com/compatible-mode/v1 | 延迟 8761.6ms | Agent=plan_execute | 策略=sliding_window | RAG注入=3段
[debug] Token: prompt=208 completion=961
```

### 11.2 后端接口

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| `POST` | `/api/workflows/{wf_id}/run` | 是 | 运行工作流（SSE） |
| `GET` | `/api/workflows/{wf_id}/runs` | 是 | 获取运行历史列表 |
| `GET` | `/api/workflows/{wf_id}/runs/{run_id}` | 是 | 获取单次运行详情 |

#### POST `/api/workflows/{wf_id}/run`（SSE）

**请求体：**
```json
{
  "input": { "input": "你好，请处理这个输入" },
  "graph_json": {
    "nodes": [...],
    "edges": [...]
  }
}
```

> `graph_json` 可选；不传则使用数据库中已保存的版本。前端运行时会传当前画布状态。

**SSE 事件格式：**

| type | 字段 | 说明 |
|------|------|------|
| `run_start` | `run_id`, `workflow_id` | 运行开始 |
| `node_start` | `node_id`, `node_type`, `label` | 节点开始执行 |
| `node_success` | `node_id`, `output`, `trace` | 节点执行成功（LLM 含 trace） |
| `node_failed` | `node_id`, `error` | 节点执行失败 |
| `log` | `time`, `level`, `message`, `node_id` | 日志条目 |
| `done` | `run_id`, `status`, `output` | 运行结束 |
| `error` | `content` | 全局错误 |

#### GET `/api/workflows/{wf_id}/runs`

**响应：**
```json
[
  {
    "id": 1,
    "workflow_id": 3,
    "status": "success",
    "input_json": { "input": "你好" },
    "output_json": { "format": "raw", "result": "..." },
    "started_at": "2026-07-02T16:35:00",
    "finished_at": "2026-07-02T16:35:15"
  }
]
```

#### GET `/api/workflows/{wf_id}/runs/{run_id}`

**响应：** 同上，额外包含 `logs_json` 数组（完整执行日志）

### 11.3 前端文件

| 文件 | 说明 |
|------|------|
| `api/execution.ts` | 执行相关 API |
| `utils/workflowSse.ts` | 工作流 SSE 客户端 |
| `types/execution.ts` | 执行相关类型 |
| `store/canvas.ts` | 执行状态（nodeExecStatus、logs、runHistory） |
| `components/canvas/ExecutionLog.vue` | 可拖拽调整大小的日志面板 |

---

## 12. 全局基础设施

### 12.1 Axios 拦截器（`utils/request.ts`）

| 功能 | 说明 |
|------|------|
| JWT 注入 | 请求头自动附加 `Authorization: Bearer <token>` |
| 全局 Loading | 请求开始显示全屏 Loading，结束关闭（登录/注册除外） |
| 错误统一提示 | ElMessage 展示错误，兼容字符串/数组 detail |
| 401 处理 | 自动登出，跳转登录页（登录页本身不重复跳转） |
| 网络错误 | 识别 Network Error、超时并友好提示 |
| 跳过选项 | `skipLoading`、`skipErrorToast` 配置项 |

### 12.2 页面过渡动画（`App.vue`）

- 登录/注册页：`fade` 淡入淡出
- 主应用页面：`slide-fade` 轻微位移 + 淡入淡出

### 12.3 响应式适配

- 登录/注册：移动端卡片宽度 100%、圆角自适应
- 顶部导航：Tab 可横向滚动，字号随屏幕缩放
- 执行日志：面板高度/宽度可拖拽调整

### 12.4 布局组件

| 组件 | 说明 |
|------|------|
| `AppHeader.vue` | 顶部导航：Logo + Tab + 用户下拉菜单（退出登录） |
| `MainLayout.vue` | 主布局：Header 固定 + router-view 内容区 |

---

## 13. 部署与运行

### 13.1 环境要求

- Node.js 18+
- Python 3.10+
- MySQL 8.0+

### 13.2 数据库初始化

```sql
-- 执行 Be_end/schema.sql 创建所有表
mysql -u root -p AiWork < Be_end/schema.sql
```

### 13.3 后端启动

```bash
cd Be_end
pip install -r requirements.txt
# 修改 config.py 中的数据库连接和百炼 API Key
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 13.4 前端启动

```bash
cd Front_end
npm install
npm run dev
# 访问 http://localhost:3000
```

### 13.5 配置项说明（`Be_end/config.py`）

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `MYSQL_HOST` | 数据库主机 | localhost |
| `MYSQL_PORT` | 数据库端口 | 3306 |
| `MYSQL_USER` | 数据库用户 | root |
| `MYSQL_PASSWORD` | 数据库密码 | *** |
| `MYSQL_DB` | 数据库名 | AiWork |
| `SECRET_KEY` | JWT 签名密钥 | 生产环境务必修改 |
| `DASHSCOPE_API_KEY` | 百炼 API Key | sk-*** |
| `DASHSCOPE_MODEL` | 默认模型 | qwen3.7-plus |
| `UPLOAD_DIR` | 文件上传目录 | uploads |

> 注：工作流 LLM 节点优先使用「模型」页用户配置；`config.py` 中的百炼配置仅作聊天模块与无用户配置时的回退。

### 13.6 健康检查

```
GET http://localhost:8000/health
→ {"status": "ok"}
```

---

## 附录：API 接口总表

| # | 方法 | 路径 | 模块 |
|---|------|------|------|
| 1 | POST | `/api/auth/register` | 认证 |
| 2 | POST | `/api/auth/login` | 认证 |
| 3 | GET | `/api/auth/me` | 认证 |
| 4 | GET | `/api/chat/conversations` | 聊天 |
| 5 | POST | `/api/chat/conversations` | 聊天 |
| 6 | GET | `/api/chat/conversations/{id}` | 聊天 |
| 7 | DELETE | `/api/chat/conversations/{id}` | 聊天 |
| 8 | POST | `/api/chat/conversations/{id}/messages` | 聊天 (SSE) |
| 9 | GET | `/api/workflows` | 工作流 |
| 10 | POST | `/api/workflows` | 工作流 |
| 11 | GET | `/api/workflows/{id}` | 工作流 |
| 12 | PUT | `/api/workflows/{id}` | 工作流 |
| 13 | DELETE | `/api/workflows/{id}` | 工作流 |
| 14 | POST | `/api/workflows/{id}/run` | 执行 (SSE) |
| 15 | GET | `/api/workflows/{id}/runs` | 执行 |
| 16 | GET | `/api/workflows/{id}/runs/{run_id}` | 执行 |
| 17 | GET | `/api/knowledge` | 知识库 |
| 18 | POST | `/api/knowledge` | 知识库 |
| 19 | DELETE | `/api/knowledge/{id}` | 知识库 |
| 20 | GET | `/api/knowledge/{id}/documents` | 知识库 |
| 21 | POST | `/api/knowledge/{id}/upload` | 知识库 |
| 22 | DELETE | `/api/knowledge/{id}/documents/{doc_id}` | 知识库 |
| 23 | GET | `/api/tools/handlers` | 工具 |
| 24 | GET | `/api/tools` | 工具 |
| 25 | POST | `/api/tools` | 工具 |
| 26 | DELETE | `/api/tools/{id}` | 工具 |
| 27 | GET | `/api/tools/{id}` | 工具 |
| 28 | POST | `/api/tools/{id}/test` | 工具 |
| 29 | GET | `/api/models` | 模型 |
| 30 | POST | `/api/models` | 模型 |
| 31 | GET | `/api/models/{id}` | 模型 |
| 32 | PUT | `/api/models/{id}` | 模型 |
| 33 | DELETE | `/api/models/{id}` | 模型 |
| 34 | POST | `/api/models/{id}/test` | 模型 |
| 35 | GET | `/health` | 系统 |

**共计 35 个 API 端点**（含 2 个 SSE 流式接口：聊天消息、工作流执行）

---

*文档结束*
