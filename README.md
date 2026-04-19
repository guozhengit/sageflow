# 🌿 SageFlow

> **智慧如流，洞察如光** — Smart Q&A Solutions

SageFlow 是一个基于 RAG（检索增强生成）技术的智能问答系统，让知识流动如水，智慧生长如叶。

---

## ✨ 核心功能

- 💬 **Precise Answers** — 准确、深度、上下文相关的回答
- 📚 **Knowledge Base** — 管理与访问你的文档资源
- 💡 **Personalized Insights** — 基于用户画像的个性化推荐

---

## 🚀 快速开始

### 环境要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| GPU | 无（使用外部 API） | 4GB 显存（本地 LLM） |
| 存储 | 40 GB | 100 GB SSD |
| Docker | ✅ 必需 | ✅ 必需 |

### 一键启动 (Windows)

```bash
# 启动所有服务
start.bat

# 停止所有服务
stop.bat
```

### Docker Compose 启动

```bash
# 复制环境变量
cp .env.example .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📦 技术架构

### 前端
- **框架**: Next.js 14 + React 18
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: Zustand

### 后端
- **框架**: FastAPI (Python 3.11)
- **RAG**: LangChain
- **任务队列**: Celery + Redis

### 数据存储
- **向量数据库**: Qdrant
- **关系数据库**: PostgreSQL
- **缓存**: Redis

### LLM
- **推理引擎**: Ollama
- **模型**: qwen2.5:3b (本地)
- **备选**: OpenAI API / 阿里云百炼

---

## 📁 项目结构

```
sageflow/
├── frontend/           # Next.js 前端
│   ├── src/
│   │   ├── app/        # 页面路由
│   │   └── components/ # 可复用组件
│   └── package.json
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── api/        # API 路由
│   │   ├── core/       # 核心配置
│   │   ├── services/   # 业务逻辑
│   │   └── models/     # 数据模型
│   └── pyproject.toml
├── postgres/           # PostgreSQL 配置
├── qdrant/             # Qdrant 配置
├── nginx/              # Nginx 配置
├── docker-compose.yml  # Docker 编排
└── docs/               # 项目文档
```

---

## 🌐 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Frontend | 3000 | Next.js 前端 |
| Backend API | 8000 | FastAPI 后端 |
| Swagger Docs | 8000/docs | API 文档 |
| Qdrant | 6333 | 向量数据库 |
| PostgreSQL | 5432 | 关系数据库 |
| Redis | 6379 | 缓存 |
| Ollama | 11434 | LLM 服务 |
| Nginx | 80/443 | 反向代理 |

---

## 📖 文档

- [技术方案与资源规划](./docs/技术方案与资源规划.md)
- [API 文档](http://localhost:8000/docs)

---

## 🤝 开发

```bash
# 前端开发
cd frontend
npm install
npm run dev

# 后端开发
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📄 License

MIT

---

*Built with ❤️ by SageFlow Team*
