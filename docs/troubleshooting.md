# SageFlow 故障排查手册

## 服务状态检查

### 快速诊断

```bash
# 检查所有服务状态
docker-compose ps

# 检查健康状态
curl -s http://localhost:8000/health | python3 -m json.tool
```

### 服务依赖关系

```
nginx → frontend → backend → postgres
                              → redis
                              → qdrant
                              → ollama
                   celery   → postgres
                              → redis
                              → qdrant
                              → ollama
```

---

## 后端 (Backend) 问题

### 后端无法启动

**症状**: `docker-compose ps` 显示 backend 反复重启

**排查步骤**:

1. 查看日志: `docker-compose logs backend`
2. 常见原因:
   - 数据库未就绪 → 检查 postgres 健康状态
   - JWT_SECRET 未设置 → 检查 `.env` 文件
   - 端口冲突 → 检查 8000 端口占用: `lsof -i :8000`

### API 返回 401

**原因**: JWT Token 过期或无效

**解决**:
1. 重新登录获取新 Token
2. 检查 JWT_SECRET 配置是否一致
3. 检查系统时间是否同步

### API 返回 429 (Too Many Requests)

**原因**: 触发限流

**解决**:
1. 等待限流窗口重置
2. 调整 `PATH_LIMITS` 配置（`backend/app/core/rate_limit.py`）
3. 检查 Redis 是否正常: `docker-compose exec redis redis-cli ping`

---

## 数据库 (PostgreSQL) 问题

### 连接失败

**排查**:
```bash
# 检查 postgres 是否运行
docker-compose exec postgres pg_isready -U sageflow

# 测试连接
docker-compose exec backend python -c "
from app.core.database import engine
import asyncio
async def test():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('DB OK:', result.scalar())
asyncio.run(test())
"
```

### 磁盘空间不足

```bash
# 检查数据库大小
docker-compose exec postgres psql -U sageflow -c "
SELECT pg_database_size('sageflow') / 1024 / 1024 AS size_mb;
"

# 清理旧数据
docker-compose exec postgres psql -U sageflow -c "VACUUM FULL;"
```

---

## 向量数据库 (Qdrant) 问题

### 集合不存在

**症状**: 日志中出现 `Collection not found`

**解决**:
```bash
# 查看现有集合
curl http://localhost:6333/collections

# 后端启动时会自动创建，重启即可
docker-compose restart backend
```

### 搜索无结果

**排查**:
1. 确认文档已处理: `curl http://localhost:8000/api/documents -H "Authorization: Bearer <token>"`
2. 检查 Celery 任务状态
3. 确认 embedding 服务正常

---

## Celery Worker 问题

### 任务卡在 PENDING

**排查**:
```bash
# 检查 Celery Worker 状态
docker-compose exec celery celery -A app.workers.celery_app inspect active

# 检查队列中的任务
docker-compose exec celery celery -A app.workers.celery_app inspect reserved

# 查看 Redis 队列
docker-compose exec redis redis-cli LLEN celery
```

### 文档处理失败

**排查**:
1. 检查 Celery 日志: `docker-compose logs celery`
2. 确认上传目录存在且可写: `docker-compose exec backend ls -la /app/uploads`
3. 确认 Ollama 和 Qdrant 可达

---

## Ollama (LLM) 问题

### 模型未加载

**症状**: API 返回 `model not found`

**解决**:
```bash
# 查看已安装模型
docker exec -it sageflow-ollama ollama list

# 拉取模型
docker exec -it sageflow-ollama ollama pull qwen2.5:3b
```

### 响应极慢

**可能原因**:
1. 内存不足 → 检查 `docker stats`
2. CPU 限制过低 → 调整 `docker-compose.yml` 中的资源限制
3. 使用外部 API 替代本地模型

---

## 前端 (Frontend) 问题

### 页面白屏

**排查**:
1. 检查浏览器控制台错误
2. 确认 `NEXT_PUBLIC_API_URL` 配置正确
3. 检查 Nginx 代理配置

### WebSocket 连接失败

**排查**:
1. 检查 Nginx WebSocket 配置（`/ws` 路径的 upgrade 头）
2. 确认后端 WebSocket 端点: `ws://localhost:8000/ws/chat`
3. 检查防火墙规则

---

## Nginx 问题

### 502 Bad Gateway

**原因**: 后端服务不可达

**排查**:
```bash
# 检查 Nginx 配置
docker-compose exec nginx nginx -t

# 检查后端是否运行
curl http://localhost:8000/health

# 查看 Nginx 错误日志
docker-compose exec nginx cat /var/log/nginx/error.log
```

---

## 紧急恢复

### 全部服务不可用

```bash
# 1. 停止所有服务
docker-compose down

# 2. 检查磁盘空间
df -h

# 3. 清理 Docker 资源
docker system prune -f

# 4. 重启服务
docker-compose up -d

# 5. 验证
curl http://localhost:8000/health
```

### 数据恢复

```bash
# 从备份恢复 PostgreSQL
cat backup_YYYYMMDD.sql | docker-compose exec -T postgres psql -U sageflow sageflow

# 重启所有依赖数据库的服务
docker-compose restart backend celery
```
