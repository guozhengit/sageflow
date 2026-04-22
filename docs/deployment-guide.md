# SageFlow 部署指南

## 环境要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| GPU | 无（使用外部 API） | 4GB 显存（本地 LLM） |
| 存储 | 40 GB | 100 GB SSD |
| Docker | 24.x+ | 24.x+ |
| Docker Compose | v2.20+ | v2.20+ |

## 快速部署

### 1. 准备环境

```bash
# 克隆项目
git clone https://github.com/your-org/sageflow.git
cd sageflow

# 复制环境变量
cp .env.example .env

# 编辑 .env，设置必要的配置
vim .env
```

### 2. 必须配置的环境变量

```env
# JWT 密钥 (必须修改！生成方式: openssl rand -hex 32)
JWT_SECRET=your-secret-key-here

# 数据库密码
DB_PASSWORD=your-strong-password

# LLM 模型
LLM_MODEL=qwen2.5:3b
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看启动状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 验证部署

```bash
# 检查健康状态
curl http://localhost:8000/health

# 检查 API 文档
# 浏览器访问 http://localhost:8000/docs

# 检查前端
# 浏览器访问 http://localhost:3000
```

## Ollama 模型拉取

首次部署后需要拉取 LLM 模型：

```bash
# 进入 Ollama 容器
docker exec -it sageflow-ollama bash

# 拉取模型
ollama pull qwen2.5:3b

# 验证模型
ollama list
```

## HTTPS 配置 (生产环境)

### 使用 Let's Encrypt

```bash
# 运行 SSL 证书生成脚本
bash scripts/generate-ssl.sh your-domain.com

# 证书会自动续期，Nginx 已配置 ACME 路径
```

### 使用自签名证书 (开发环境)

```bash
bash scripts/generate-ssl.sh localhost --self-signed
```

## 数据库迁移

```bash
# 运行迁移
docker-compose exec backend alembic upgrade head

# 查看当前版本
docker-compose exec backend alembic current

# 回滚一个版本
docker-compose exec backend alembic downgrade -1
```

## 备份与恢复

### 数据库备份

```bash
# 创建备份
docker-compose exec postgres pg_dump -U sageflow sageflow > backup_$(date +%Y%m%d).sql

# 恢复备份
cat backup_20260422.sql | docker-compose exec -T postgres psql -U sageflow sageflow
```

### 向量数据库备份

```bash
# Qdrant 快照
curl -X POST http://localhost:6333/snapshots
# 快照存储在 qdrant_data volume 中
```

### 全量备份

```bash
# 备份所有 Docker volumes
docker run --rm -v sageflow_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres_backup_$(date +%Y%m%d).tar.gz -C /data .
```

## 扩容

### 水平扩展 Backend

```bash
# 启动多个 backend 实例
docker-compose up -d --scale backend=3
```

> 注意：扩展后需要更新 Nginx upstream 配置

### 增加 Celery Worker

```bash
docker-compose up -d --scale celery=3
```

## 监控

### 健康检查端点

| 端点 | 说明 |
|------|------|
| `GET /health` | 综合健康检查（DB + Redis + Qdrant + Ollama） |
| `GET /metrics` | Prometheus 格式指标 |
| `GET /api/stats/system` | 系统统计（管理员） |

### 日志查看

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f celery

# 查看最近 100 行
docker-compose logs --tail=100 backend
```

## 常见问题

### Q: Ollama 模型加载失败

```bash
# 检查 Ollama 状态
docker-compose logs ollama

# 手动拉取模型
docker exec -it sageflow-ollama ollama pull qwen2.5:3b
```

### Q: Qdrant 连接失败

```bash
# 检查 Qdrant 状态
curl http://localhost:6333/collections

# 重启 Qdrant
docker-compose restart qdrant
```

### Q: 数据库迁移失败

```bash
# 检查当前迁移状态
docker-compose exec backend alembic current

# 强制标记当前版本（谨慎使用）
docker-compose exec backend alembic stamp head
```
