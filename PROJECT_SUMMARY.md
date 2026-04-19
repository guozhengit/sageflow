# 📊 SageFlow 项目总结

> 项目创建时间：2026-04-15
> 最后更新：2026-04-16
> 状态：✅ 核心功能完整 + 质量增强完成

---

## 优化记录

### ✅ 已完成优化

| # | 优化项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | 深色/浅色主题切换 | ✅ 完成 | ThemeProvider + CSS 变量 |
| 2 | 快捷键支持 | ✅ 完成 | Enter 发送, Ctrl+N 新对话 |
| 3 | 数据统计面板 | ✅ 完成 | 用户统计 API + 前端页面 |
| 4 | 移动端响应式 | ✅ 完成 | 侧边栏抽屉 + 自适应布局 |
| 5 | API 文档完善 | ✅ 完成 | Swagger 注解 + 字段描述 |
| 6 | 认证系统优化 | ✅ 完成 | get_current_user 统一管理 |
| 7 | 错误边界组件 | ✅ 完成 | ErrorBoundary 捕获异常 |
| 8 | API 请求重试 | ✅ 完成 | axios-retry 指数退避 |
| 9 | 主题系统增强 | ✅ 完成 | 支持跟随系统主题 |
| 10 | 前端测试框架 | ✅ 完成 | Jest + Testing Library |
| 11 | 后端测试框架 | ✅ 完成 | pytest + pytest-asyncio |
| 12 | 环境配置完善 | ✅ 完成 | .env + 测试配置 |

---

## 项目概述

SageFlow 是一个基于 RAG（检索增强生成）技术的智能问答系统，专为本地部署优化，适配 i7 4核/16GB/4GB GPU 服务器配置。

---

## 已完成功能

### ✅ Phase 1: 基础架构

| 任务 | 状态 | 说明 |
|------|------|------|
| 项目目录结构 | ✅ 完成 | 前后端分离架构 |
| Docker Compose | ✅ 完成 | 8 个服务一键部署 |
| FastAPI 后端 | ✅ 完成 | RESTful API 框架 |
| Next.js 前端 | ✅ 完成 | 4 个页面 UI |
| 数据库配置 | ✅ 完成 | PostgreSQL + Redis |
| Ollama 集成 | ✅ 完成 | 本地 LLM 服务 |

### ✅ Phase 2: 核心 RAG

| 任务 | 状态 | 说明 |
|------|------|------|
| LLM 服务 | ✅ 完成 | Ollama API 封装 |
| 向量存储 | ✅ 完成 | Qdrant 集成 |
| Embedding | ✅ 完成 | MiniLM 多语言模型 |
| RAG Pipeline | ✅ 完成 | 检索+生成核心逻辑 |
| 文档处理 | ✅ 完成 | PDF/DOCX/TXT 解析 |
| Celery 任务 | ✅ 完成 | 异步文档索引 |

### 📋 Phase 3-5: 待完成

| 任务 | 状态 | 优先级 |
|------|------|--------|
| 用户认证系统 | ⏳ 待开发 | 中 |
| 会话管理 | ⏳ 待开发 | 中 |
| 流式响应 | ⏳ 待开发 | 高 |
| 前端优化 | ⏳ 待开发 | 中 |
| 单元测试 | ⏳ 待开发 | 低 |
| 性能优化 | ⏳ 待开发 | 高 |

---

## 技术栈

### 前端
- **Next.js 14** - React 元框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 原子化样式
- **Axios** - HTTP 客户端

### 后端
- **FastAPI** - 高性能异步框架
- **LangChain** - RAG 框架
- **Celery** - 异步任务队列
- **PyMuPDF** - PDF 解析

### 数据存储
- **Qdrant** - 向量数据库 (Rust)
- **PostgreSQL 16** - 关系数据库
- **Redis 7** - 缓存/消息队列

### AI/ML
- **Ollama** - LLM 推理引擎
- **Qwen2.5-3B** - 大语言模型
- **MiniLM** - 文本嵌入模型

---

## 项目结构

```
sageflow/
├── frontend/                   # Next.js 前端
│   ├── src/
│   │   ├── app/                # 页面路由
│   │   │   ├── page.tsx        # 首页
│   │   │   ├── chat/page.tsx   # 问答页
│   │   │   ├── knowledge/page.tsx  # 知识库
│   │   │   └── profile/page.tsx    # 用户画像
│   │   └── app/globals.css     # 全局样式
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   │   ├── chat.py         # 问答接口
│   │   │   ├── documents.py    # 文档接口
│   │   │   └── users.py        # 用户接口
│   │   ├── core/               # 核心配置
│   │   │   ├── config.py       # 配置管理
│   │   │   └── database.py     # 数据库
│   │   ├── services/           # 业务逻辑
│   │   │   ├── rag_service.py  # RAG 服务
│   │   │   ├── llm_service.py  # LLM 服务
│   │   │   ├── vector_store.py # 向量存储
│   │   │   ├── embedding.py    # Embedding
│   │   │   └── document_processor.py  # 文档处理
│   │   ├── models/             # 数据模型
│   │   └── workers/            # 异步任务
│   │       ├── celery_app.py   # Celery 配置
│   │       └── tasks.py        # 任务定义
│   ├── pyproject.toml
│   └── Dockerfile
│
├── postgres/
│   └── init.sql                # 数据库初始化
├── qdrant/                     # Qdrant 配置
├── nginx/
│   └── nginx.conf              # Nginx 配置
├── docs/
│   └── 技术方案与资源规划.md
├── docker-compose.yml          # Docker 编排
├── .env.example                # 环境变量模板
├── start.bat                   # Windows 启动脚本
├── stop.bat                    # Windows 停止脚本
├── README.md                   # 项目说明
└── QUICKSTART.md               # 快速启动
```

---

## 服务端口

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| Nginx | 80 | HTTP | 反向代理 |
| Frontend | 3000 | HTTP | Next.js 前端 |
| Backend | 8000 | HTTP | FastAPI 后端 |
| Qdrant | 6333 | HTTP | 向量数据库 |
| PostgreSQL | 5432 | TCP | 关系数据库 |
| Redis | 6379 | TCP | 缓存 |
| Ollama | 11434 | HTTP | LLM 服务 |

---

## API 端点

### 用户
- `GET /api/users/` - 获取用户列表
- `POST /api/users/register` - 用户注册
- `POST /api/users/login` - 用户登录
- `GET /api/users/profile` - 获取用户画像

### 文档
- `GET /api/documents/` - 获取文档列表
- `POST /api/documents/upload` - 上传文档
- `DELETE /api/documents/{id}` - 删除文档
- `POST /api/documents/{id}/index` - 索引文档

### 问答
- `POST /api/chat/message` - 发送消息 (RAG)
- `POST /api/chat/stream` - 流式消息
- `GET /api/chat/conversations` - 获取对话列表

---

## 资源使用

### 运行时资源

| 服务 | CPU | 内存 | GPU |
|------|-----|------|-----|
| Ollama | 2.0 | 3-4GB | 3GB VRAM |
| Qdrant | 0.5 | 2GB | - |
| PostgreSQL | 0.5 | 1GB | - |
| Redis | 0.25 | 512MB | - |
| Backend | 1.0 | 2GB | - |
| Frontend | 0.5 | 1GB | - |
| **总计** | **~6.5** | **~13GB** | **~3GB** |

### 磁盘空间

| 用途 | 空间 |
|------|------|
| Docker 镜像 | ~20GB |
| 模型文件 | ~5GB |
| 向量数据 | ~50GB (预估) |
| 数据库 | ~10GB |
| 文档存储 | ~50GB |
| 系统 | ~30GB |
| **总计** | **~165GB** |

---

## 性能指标

### 预期性能

| 指标 | 目标 |
|------|------|
| 问答响应时间 | < 5 秒 |
| 文档索引速度 | ~100 页/分钟 |
| 并发用户数 | 10-20 |
| 最大文档大小 | 50MB |
| 支持文档格式 | PDF, DOCX, TXT |

---

## 下一步开发计划

### 短期 (1-2 周)
1. ✅ 基础架构搭建
2. ✅ 核心 RAG 功能
3. ⏳ 流式响应优化
4. ⏳ 前端交互完善

### 中期 (2-4 周)
1. ⏳ 用户认证系统 (JWT)
2. ⏳ 会话管理
3. ⏳ 文档版本控制
4. ⏳ 个性化推荐

### 长期 (1-3 月)
1. ⏳ 多模型支持
2. ⏳ 分布式部署
3. ⏳ 监控告警
4. ⏳ 性能压测

---

## 已知限制

1. **CPU 4核** - 文档处理速度较慢，建议异步处理
2. **4GB GPU** - 仅支持 3B 级别模型，无法运行更大模型
3. **无认证** - 当前为 Demo 版本，无用户认证
4. **单用户** - 暂未实现多用户隔离

---

## 贡献者

- AI Assistant (Qwen Code)

---

*最后更新: 2026-04-15*
