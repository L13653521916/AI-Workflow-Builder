---
name: AI Workflow Builder 前端开发计划
overview: Vue 3 + Element Plus + Vue Flow + Tailwind CSS 构建 AI Workflow Builder 前端,包含认证系统、聊天界面、画布编辑器、知识库管理、工具调用等模块,采用方案A(并列切换)架构。
todos:
  - id: phase0
    content: "Phase 0: 项目初始化 (1-2天) - Vue3+TS脚手架、依赖安装、目录结构、路由配置、Vite配置、Tailwind/Element Plus集成"
    status: in_progress
  - id: phase1
    content: "Phase 1: 认证系统 (1-2天) - 注册/登录页面、JWT令牌管理、路由守卫、axios拦截器"
    status: pending
  - id: phase2
    content: "Phase 2: 整体布局与导航 (1天) - 主布局(顶部导航+侧边栏)、聊天/画布/知识库 Tab 切换、用户菜单"
    status: pending
  - id: phase3
    content: "Phase 3: 聊天界面 (2-3天) - 消息列表、输入框、SSE流式输出、Markdown渲染、对话历史侧边栏"
    status: pending
  - id: phase4
    content: "Phase 4: 画布编辑器 (3-4天) - Vue Flow集成、节点拖拽/连线、节点配置面板、节点类型注册、工作流保存/加载"
    status: pending
  - id: phase5
    content: "Phase 5: 文件上传与知识库 (1-2天) - 文件上传组件、知识库列表/创建、文档管理、上传进度展示"
    status: pending
  - id: phase6
    content: "Phase 6: 工具调用 (1-2天) - 工具列表展示、工具详情/测试、工具节点嵌入画布"
    status: pending
  - id: phase7
    content: "Phase 7: 执行与监控 (1-2天) - 工作流运行、实时状态推送(SSE)、执行日志面板、节点状态高亮"
    status: pending
  - id: phase8
    content: "Phase 8: 打磨与优化 (1-2天) - 响应式适配、错误处理、loading状态、整体联调"
    status: pending
isProject: false
---

# AI Workflow Builder 前端开发计划

## 技术栈

| 技术 | 选型 |
|------|------|
| 框架 | Vue 3 + TypeScript |
| 状态管理 | Vuex 4 |
| UI 组件库 | Element Plus |
| 画布 | Vue Flow (@vue-flow/core) |
| 样式 | Tailwind CSS |
| HTTP | Axios + SSE |
| 构建 | Vite |

## 页面结构 (方案A: 并列切换)

```
┌──────────────────────────────────────────────────────┐
│  Logo     [聊天] [画布] [知识库] [工具]      用户名 ▼ │
├──────────────────────────────────────────────────────┤
│                                                      │
│              对应 Tab 的内容区域                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## 前端目录结构

```
frontend/
├── public/
├── src/
│   ├── api/                    # API 接口封装
│   │   ├── auth.ts             # 认证相关接口
│   │   ├── chat.ts             # 聊天接口
│   │   ├── workflow.ts         # 工作流 CRUD
│   │   ├── knowledge.ts        # 知识库接口
│   │   └── tools.ts            # 工具接口
│   ├── assets/                 # 静态资源
│   ├── components/             # 通用组件
│   │   ├── layout/             # 布局组件
│   │   │   ├── AppHeader.vue   # 顶部导航栏
│   │   │   └── AppSidebar.vue  # 侧边栏
│   │   ├── chat/               # 聊天组件
│   │   │   ├── MessageList.vue     # 消息列表
│   │   │   ├── MessageItem.vue     # 单条消息
│   │   │   ├── ChatInput.vue       # 输入框
│   │   │   └── ConversationList.vue# 对话历史
│   │   ├── canvas/             # 画布组件
│   │   │   ├── WorkflowCanvas.vue  # 画布主容器
│   │   │   ├── NodePalette.vue     # 节点面板(拖拽源)
│   │   │   ├── NodeConfigPanel.vue # 节点配置面板
│   │   │   └── nodes/              # 各类节点组件
│   │   │       ├── LLMNode.vue
│   │   │       ├── RAGNode.vue
│   │   │       ├── ToolNode.vue
│   │   │       ├── ConditionNode.vue
│   │   │       ├── StartNode.vue
│   │   │       └── EndNode.vue
│   │   ├── knowledge/          # 知识库组件
│   │   │   ├── KBList.vue      # 知识库列表
│   │   │   ├── KBCreate.vue    # 创建知识库
│   │   │   └── DocUpload.vue   # 文档上传
│   │   ├── tools/              # 工具组件
│   │   │   ├── ToolList.vue    # 工具列表
│   │   │   └── ToolDetail.vue  # 工具详情/测试
│   │   └── common/             # 通用组件
│   │       ├── MarkdownRenderer.vue  # Markdown 渲染
│   │       ├── LoadingSpinner.vue
│   │       └── FileUploader.vue      # 文件上传
│   ├── views/                  # 页面视图
│   │   ├── LoginView.vue       # 登录页
│   │   ├── RegisterView.vue    # 注册页
│   │   ├── ChatView.vue        # 聊天页
│   │   ├── CanvasView.vue      # 画布页
│   │   ├── KnowledgeView.vue   # 知识库页
│   │   └── ToolsView.vue       # 工具页
│   ├── store/                  # Vuex 状态管理
│   │   ├── index.ts
│   │   ├── auth.ts             # 用户认证状态
│   │   ├── chat.ts             # 聊天状态
│   │   ├── canvas.ts           # 画布状态
│   │   └── knowledge.ts        # 知识库状态
│   ├── router/                 # 路由配置
│   │   └── index.ts
│   ├── utils/                  # 工具函数
│   │   ├── request.ts          # Axios 封装 + JWT 拦截器
│   │   └── sse.ts              # SSE 连接管理
│   ├── types/                  # TypeScript 类型定义
│   │   ├── auth.ts
│   │   ├── chat.ts
│   │   ├── workflow.ts
│   │   └── knowledge.ts
│   ├── App.vue
│   └── main.ts
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

---

## Phase 0: 项目初始化 (1-2天)

**目标:** 项目骨架搭建完毕,所有依赖就绪。

**任务清单:**
- [ ] 用 Vite 创建 Vue 3 + TypeScript 项目
- [ ] 安装依赖: `element-plus`, `@vue-flow/core`, `vuex@4`, `axios`, `tailwindcss`
- [ ] 配置 Tailwind CSS
- [ ] 配置 Element Plus (按需导入)
- [ ] 创建目录结构
- [ ] 配置 Vite (代理、路径别名)
- [ ] 配置 TypeScript

**关键文件:**
- `vite.config.ts` - Vite 配置,开发代理 `/api` → `http://localhost:8000`
- `tailwind.config.js` - Tailwind 配置

---

## Phase 1: 认证系统 (1-2天)

**目标:** 注册/登录完整闭环,JWT 令牌自动管理。

**任务清单:**
- [ ] LoginView.vue - 登录表单(用户名+密码)
- [ ] RegisterView.vue - 注册表单(用户名+邮箱+密码+确认密码)
- [ ] `api/auth.ts` - login / register / getMe 接口
- [ ] `store/auth.ts` - user 状态、token 存储(localStorage)
- [ ] `utils/request.ts` - Axios 实例 + 请求拦截器(自动带 JWT)
- [ ] 路由守卫 - 未登录跳转 /login

**页面交互:**
```
注册页面:
┌──────────────────────┐
│    创建账号           │
│  ┌────────────────┐  │
│  │ 用户名          │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ 邮箱            │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ 密码            │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ 确认密码        │  │
│  └────────────────┘  │
│  [ 注册 ]            │
│  已有账号? 去登录     │
└──────────────────────┘
```

---

## Phase 2: 整体布局与导航 (1天)

**目标:** 主框架搭建完成,Tab 切换可用。

**任务清单:**
- [ ] AppHeader.vue - Logo + 导航 Tab + 用户菜单
- [ ] 路由配置 - /chat, /canvas, /knowledge, /tools
- [ ] 主布局 - Header 固定顶部,下方为内容区
- [ ] 用户下拉菜单 - 个人信息、退出登录

**布局结构:**
```
AppHeader.vue:
┌─────────────────────────────────────────────┐
│ 🤖 AI Workflow Builder                      │
│      [聊天] [画布] [知识库] [工具]           │
│                                 [ 用户名 ▼ ] │
│                              ├── 个人信息    │
│                              └── 退出登录    │
└─────────────────────────────────────────────┘
```

---

## Phase 3: 聊天界面 (2-3天)

**目标:** 完整的对话体验,支持流式输出。

**任务清单:**
- [ ] ChatView.vue - 页面容器(左侧对话列表 + 右侧聊天区)
- [ ] ConversationList.vue - 对话历史列表,新建对话
- [ ] MessageList.vue - 消息滚动列表,自动滚到底部
- [ ] MessageItem.vue - 单条消息(区分用户/AI/系统消息)
- [ ] ChatInput.vue - 输入框 + 发送按钮 + 附件按钮
- [ ] MarkdownRenderer.vue - AI 回复的 Markdown 渲染(代码高亮)
- [ ] SSE 流式输出 - 后端逐字推送,AI 打字效果
- [ ] `api/chat.ts` - sendMessage / getConversations / getMessages
- [ ] `store/chat.ts` - 当前对话、消息列表、流式状态

**页面交互:**
```
┌──────────────┬──────────────────────────────┐
│ 对话列表      │                              │
│              │  用户: 帮我分析这篇论文        │
│ [+ 新建对话]  │  ────────────────────────     │
│              │  AI: 好的,我来分析...          │
│  对话1       │                              │
│  对话2       │  用户: 总结一下关键结论        │
│  对话3       │  ────────────────────────     │
│              │  AI: 以下是关键结论:           │
│              │    1. ...                     │
│              │    2. ...                     │
│              │                              │
│              │  ┌──────────────────────┐    │
│              │  │ 输入消息...      📎 ▶│    │
│              │  └──────────────────────┘    │
└──────────────┴──────────────────────────────┘
```

---

## Phase 4: 画布编辑器 (3-4天) - 核心

**目标:** 可视化工作流搭建,节点拖拽+连线+配置。

**任务清单:**
- [ ] CanvasView.vue - 画布页面容器
- [ ] NodePalette.vue - 左侧节点面板(拖拽源)
- [ ] WorkflowCanvas.vue - Vue Flow 画布主组件
- [ ] 节点组件开发:
  - [ ] StartNode.vue - 起始节点(输入参数定义)
  - [ ] LLMNode.vue - LLM 推理节点(模型选择+Prompt)
  - [ ] RAGNode.vue - RAG 检索节点(知识库选择)
  - [ ] ToolNode.vue - 工具调用节点(工具选择+参数)
  - [ ] ConditionNode.vue - 条件判断节点
  - [ ] EndNode.vue - 输出节点
- [ ] NodeConfigPanel.vue - 右侧节点配置面板(动态表单)
- [ ] 工作流保存/加载 - saveWorkflow / loadWorkflow
- [ ] `store/canvas.ts` - 画布状态(节点列表、连线、选中节点)
- [ ] `api/workflow.ts` - CRUD 接口

**画布交互:**
```
┌─────────┬─────────────────────┬─────────────┐
│ 节点面板 │                     │ 节点配置    │
│         │                     │             │
│ [起始]  │   ┌───┐    ┌───┐   │ 模型:       │
│ [LLM]  │   │起始│ → │LLM│   │ [GPT-4 ▼]  │
│ [RAG]  │   └───┘    └───┘   │             │
│ [工具]  │       ↘    ↙       │ Prompt:     │
│ [条件]  │       ┌────┐       │ [文本框]    │
│ [输出]  │       │输出│       │             │
│         │       └────┘       │ [保存]      │
│         │                     │ [运行]      │
└─────────┴─────────────────────┴─────────────┘
```

---

## Phase 5: 文件上传与知识库 (1-2天)

**目标:** 知识库管理完整闭环。

**任务清单:**
- [ ] KnowledgeView.vue - 知识库页面
- [ ] KBList.vue - 知识库卡片列表
- [ ] KBCreate.vue - 创建知识库(名称+描述)
- [ ] DocUpload.vue - 文件上传(PDF/TXT/MD)
- [ ] FileUploader.vue - 通用上传组件(进度条+拖拽上传)
- [ ] `api/knowledge.ts` - createKB / uploadDoc / listDocs / deleteDoc
- [ ] `store/knowledge.ts` - 知识库列表、当前知识库、文档列表

---

## Phase 6: 工具调用 (1-2天)

**目标:** 工具浏览、测试,可嵌入画布节点。

**任务清单:**
- [ ] ToolsView.vue - 工具页面
- [ ] ToolList.vue - 工具卡片列表(按类别筛选)
- [ ] ToolDetail.vue - 工具详情 + 在线测试
- [ ] 工具节点集成到画布(ToolNode 调用工具 API)
- [ ] `api/tools.ts` - listTools / getToolDetail / testTool

---

## Phase 7: 执行与监控 (1-2天)

**目标:** 工作流运行,实时反馈执行状态。

**任务清单:**
- [ ] 工作流执行按钮 - 触发后端执行
- [ ] SSE 实时状态推送 - 节点状态实时更新
- [ ] 节点状态高亮 - 执行中(黄色)、成功(绿色)、失败(红色)
- [ ] ExecutionLog.vue - 底部日志面板(可折叠)
- [ ] 执行结果展示 - 节点输出内容查看
- [ ] 运行历史 - 查看历史执行记录

---

## Phase 8: 打磨与优化 (1-2天)

**目标:** 提升用户体验,准备联调。

**任务清单:**
- [ ] 全局 Loading 状态管理
- [ ] 全局错误处理(axios 拦截器 + 统一提示)
- [ ] 响应式适配(移动端/平板)
- [ ] 页面过渡动画
- [ ] 前后端联调
- [ ] Bug 修复

---

## 开发顺序与依赖关系

```
Phase 0 (初始化)
    ↓
Phase 1 (认证)  ─────────────────┐
    ↓                            │
Phase 2 (布局) ← 需要认证完成    │
    ↓                            │
    ├── Phase 3 (聊天)           │
    ├── Phase 4 (画布) ← 核心    │
    ├── Phase 5 (知识库)         │
    └── Phase 6 (工具)           │
         ↓                       │
    Phase 7 (执行监控)           │
         ↓                       │
    Phase 8 (打磨) ← 全部完成后  │
```

Phase 3-6 可以并行开发,因为它们是独立的 Tab 页面。

---

## MVP 范围 (推荐先做)

**Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 (核心)**

这5个 Phase 完成后,你就有一个可运行的最小产品:
- 可以登录/注册
- 可以切换聊天/画布模式
- 可以在画布上搭建简单工作流
- 可以进行基础对话