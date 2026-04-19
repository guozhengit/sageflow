# 🚀 SageFlow 快速启动指南

## 前置条件

确保你的机器已安装以下软件：

- ✅ **Docker Desktop** (Windows) - [下载链接](https://www.docker.com/products/docker-desktop/)
- ✅ **Git** (可选，用于版本控制)

## 一键启动

### Windows 用户

双击运行 `start.bat` 文件，或在命令行执行：

```bash
start.bat
```

### 手动启动

```bash
# 1. 复制环境变量
copy .env.example .env

# 2. 启动所有服务
docker-compose up -d

# 3. 等待服务就绪（首次需要下载模型，约 2-5 分钟）
```

## 验证服务

启动后访问以下地址验证：

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端首页 | http://localhost:3000 | SageFlow 主页 |
| 问答界面 | http://localhost:3000/chat | 智能问答 |
| 知识库 | http://localhost:3000/knowledge | 文档管理 |
| 用户画像 | http://localhost:3000/profile | 个性化设置 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| Qdrant | http://localhost:6333/dashboard | 向量数据库 |

## 常见问题

### 1. 端口被占用

如果 3000/8000/5432 等端口被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "3001:3000"  # 改为其他端口
```

### 2. 模型下载失败

手动下载模型：

```bash
docker-compose run --rm ollama ollama pull qwen2.5:3b
```

### 3. 内存不足

在 `docker-compose.yml` 中调低资源限制：

```yaml
deploy:
  resources:
    limits:
      memory: 2G  # 调低内存
```

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（会清除所有数据）
docker-compose down -v
```

## 开发模式

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 下一步

- 📖 阅读 [技术方案文档](./docs/技术方案与资源规划.md)
- 🔌 查看 [API 文档](http://localhost:8000/docs)
- 💬 在问答界面测试 RAG 功能
- 📚 上传文档到知识库

---

*如有问题，请查看日志或提交 Issue*
