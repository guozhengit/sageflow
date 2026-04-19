# 📝 SageFlow 更新日志

## v0.8.0 (2026-04-17) - 企业级部署版本

### 🧪 测试增强

#### 后端测试
- ✅ 添加 `test_documents.py` 文档 API 测试
- ✅ 添加 `test_rag_service.py` RAG 服务测试
- ✅ 添加 `test_vector_store.py` 向量存储测试
- ✅ 测试 Fixtures 增强 (admin_user, test_conversation)

#### 测试覆盖
- ✅ 认证/授权测试
- ✅ API 端点测试
- ✅ 服务层单元测试
- ✅ Mock 外部依赖

### 📚 文档完善

#### API 文档
- ✅ 添加 `docs/api.md` 详细 API 文档
- ✅ 所有端点请求/响应示例
- ✅ 认证方式说明
- ✅ 错误码参考
- ✅ 限流规则说明
- ✅ WebSocket API 文档

### ⚡ 性能优化

#### 模型懒加载
- ✅ Embedding 服务懒加载实现
- ✅ Reranker 服务懒加载实现
- ✅ 首次使用时才加载模型
- ✅ 预加载接口支持

### ☸️ Kubernetes 部署

#### K8s 配置
- ✅ Namespace 配置
- ✅ ConfigMap 和 Secrets
- ✅ PostgreSQL StatefulSet
- ✅ Redis Deployment
- ✅ Qdrant Deployment + PVC
- ✅ Ollama Deployment + PVC
- ✅ Backend Deployment (多副本)
- ✅ Frontend Deployment (多副本)
- ✅ Celery Worker Deployment
- ✅ Ingress (HTTPS + WebSocket)
- ✅ HorizontalPodAutoscaler
- ✅ PodDisruptionBudget

#### 生产特性
- ✅ 资源限制配置
- ✅ 健康检查探针
- �️ 自动扩缩容 (HPA)
- ✅ 滚动更新支持
- �️ 初始化容器等待依赖

---

## v0.7.0 (2026-04-17) - 安全增强版本

### 🔒 安全性改进

#### JWT 安全增强
- ✅ 移除 JWT_SECRET 硬编码默认值
- ✅ 强制从环境变量获取密钥
- ✅ 添加密钥长度检查 (≥32 字符)
- ✅ 生产环境配置警告

#### 权限控制
- ✅ 用户列表 API 添加管理员权限检查
- ✅ 新增 `require_admin` 依赖注入
- ✅ User 模型添加 `is_admin` 字段

#### 配置安全
- ✅ 添加 `.gitignore` 排除敏感文件
- ✅ 创建 `.env.example` 示例配置
- ✅ 敏感配置不纳入版本控制

### 🔧 API 完善

#### 文档 API 认证
- ✅ 所有文档端点添加认证依赖
- ✅ 文档上传关联用户 ID
- ✅ 操作日志记录

#### 错误处理改进
- ✅ 文档删除时向量清理错误记录日志
- ✅ 返回详细的删除状态信息

### 🌐 HTTPS 配置

#### Nginx SSL
- ✅ 支持 HTTPS/SSL 配置
- ✅ HTTP 自动重定向到 HTTPS
- ✅ TLS 1.2/1.3 支持
- ✅ 安全头配置 (HSTS, X-Frame-Options 等)
- ✅ Gzip 压缩启用
- ✅ WebSocket 代理支持
- ✅ 自签名证书生成脚本

### 🐛 Bug 修复

- ✅ 修复 Celery 任务异步调用问题 (`asyncio.run()`)
- ✅ 修复文档 API 缺少认证依赖
- ✅ 修复用户列表 API 无权限控制

---

## v0.6.0 (2026-04-17) - 运维增强版本

### 🔍 监控与可观测性

#### 健康检查增强
- ✅ `/health` 端点支持详细模式 (`?detailed=true`)
- ✅ 检查 PostgreSQL、Redis、Qdrant、Ollama 服务状态
- ✅ 返回各服务延迟和错误信息
- ✅ 服务连接状态汇总

#### Prometheus 监控指标
- ✅ `/metrics` 端点输出 Prometheus 格式指标
- ✅ HTTP 请求计数 (`sageflow_http_requests_total`)
- ✅ 请求延迟直方图 (`sageflow_http_request_duration_seconds`)
- ✅ 进程内存和 CPU 使用率
- ✅ 自动请求路径简化 (移除动态 ID)

#### 结构化日志
- ✅ JSON 格式日志 (生产环境)
- ✅ 彩色格式日志 (开发环境)
- ✅ 请求 ID 追踪
- ✅ 请求/响应日志中间件

### 🌐 WebSocket 支持

#### 实时通信
- ✅ `/ws/chat` 聊天 WebSocket 端点
- ✅ 流式响应实时推送
- ✅ 来源信息实时展示
- ✅ JWT Token 认证
- ✅ 连接管理器 (多用户、多会话)

#### 消息类型
- ✅ `chat` - 发送聊天消息
- ✅ `ping/pong` - 心跳检测
- ✅ `token` - 流式 token 推送
- ✅ `source` - 来源信息推送
- ✅ `complete` - 响应完成通知
- ✅ `error` - 错误信息

### 📚 API 文档增强

#### OpenAPI/Swagger
- ✅ 完整的 API 描述文档
- ✅ Tags 分组 (users, documents, chat, stats, llm, websocket)
- ✅ `/docs` Swagger UI
- ✅ `/redoc` ReDoc UI
- ✅ 认证说明和示例

### 🔒 安全与限流

#### API 限流
- ✅ 滑动窗口限流算法
- ✅ Lua 脚本原子操作
- ✅ 按端点配置限流规则
- ✅ 默认: 100 请求/分钟
- ✅ 登录: 5 请求/分钟
- ✅ 注册: 3 请求/分钟
- ✅ 聊天: 30 请求/分钟

#### Redis 缓存
- ✅ LLM 响应缓存
- ✅ 向量检索结果缓存
- ✅ 可配置的缓存 TTL
- ✅ 缓存命中率统计

### 🗄️ 数据库优化

#### Alembic 迁移
- ✅ 数据库版本管理
- ✅ 初始迁移脚本
- ✅ 向上/向下迁移支持

#### 连接池优化
- ✅ 连接池大小: 10 + 20 overflow
- ✅ 连接回收: 3600 秒
- ✅ 连接超时: 30 秒
- ✅ 连接事件监听

### 🐳 Docker 增强

#### 镜像优化
- ✅ 多阶段构建
- ✅ 非 root 用户运行
- ✅ 健康检查配置
- ✅ 最小化镜像体积

#### docker-compose
- ✅ 健康检查 start_period
- ✅ JSON 日志轮转 (10MB x 3)
- ✅ 资源限制配置
- ✅ 服务依赖管理

### 🚀 CI/CD

#### GitHub Actions
- ✅ 自动化测试流程
- ✅ 代码质量检查 (flake8, black, ESLint)
- ✅ Docker 镜像构建
- ✅ 自动部署支持

---

## v0.5.0 (2026-04-16) - 质量增强版本

### 🔧 代码质量改进

#### 认证系统优化
- ✅ 将 `get_current_user` 移至 `auth.py` 统一管理
- ✅ 添加 `get_current_user_optional` 可选认证依赖
- ✅ 完善认证错误响应头 (WWW-Authenticate)
- ✅ 移除重复代码，提升可维护性

#### 错误处理
- ✅ 添加 React ErrorBoundary 组件
- ✅ 捕获组件树错误，显示友好错误页面
- ✅ 支持自定义 fallback 和重试功能

#### API 可靠性
- ✅ 集成 axios-retry 自动重试机制
- ✅ 指数退避策略 (1s → 2s → 4s)
- ✅ 5xx 服务器错误自动重试
- ✅ 网络错误自动重试

#### 主题系统增强
- ✅ 支持 'system' 主题 (跟随系统)
- ✅ 监听系统主题变化
- ✅ 完善的主题持久化 (localStorage)
- ✅ resolvedTheme 返回实际主题

### 🧪 测试框架

#### 前端测试
- ✅ Jest + React Testing Library 配置
- ✅ ErrorBoundary 组件测试
- ✅ Auth 工具函数测试
- ✅ localStorage mock 配置

#### 后端测试
- ✅ pytest + pytest-asyncio 配置
- ✅ 用户 API 测试 (注册/登录/画像)
- ✅ 认证工具测试 (密码/JWT)
- ✅ Chat API 测试
- ✅ SQLite 内存数据库测试配置

### 📁 配置文件

- ✅ 添加 `.env` 生产环境配置
- ✅ 添加 `requirements-test.txt` 测试依赖
- ✅ 添加 `pytest.ini` 测试配置
- ✅ 添加 `jest.config.ts` Jest 配置
- ✅ 添加 `jest.setup.ts` Jest 设置

---

## v0.4.0 (2026-04-15) - RAG 增强版本

### 🤖 RAG Pipeline 增强

#### 流式响应
- ✅ 前端 SSE 流式解析
- ✅ 逐字显示回答
- ✅ 实时来源展示
- ✅ 错误处理

#### 检索增强
- ✅ 混合检索 (BM25 + Vector)
- ✅ 重排序服务 (Cross-Encoder)
- ✅ 相似度阈值配置
- ✅ RRF 结果融合

#### 对话理解
- ✅ 多轮对话上下文
- ✅ 查询重写 (指代消解)
- ✅ 历史感知的 Prompt 构建

#### 模型管理
- ✅ 多模型切换 (Qwen/Phi/Llama)
- ✅ 模型列表 API
- ✅ 运行时模型切换

---

## v0.3.0 (2026-04-15) - 优化版本

### ✨ 新增优化

#### 主题系统
- ✅ 深色/浅色主题切换
- ✅ ThemeProvider 上下文
- ✅ localStorage 持久化主题偏好
- ✅ ThemeToggle 组件

#### 快捷键
- ✅ Enter 快速发送消息
- ✅ Ctrl+N 新建对话
- ✅ 可配置快捷键 Hook

#### 数据统计
- ✅ 用户统计 API (对话数、消息数)
- ✅ 系统统计 API (用户数、向量数)
- ✅ 数据统计页面 UI
- ✅ 账户信息展示

#### 响应式设计
- ✅ 移动端侧边栏抽屉
- ✅ 自适应布局 (sm/md/lg)
- ✅ 移动端菜单按钮
- ✅ 触摸友好的交互

#### API 文档
- ✅ Swagger Field 注解
- ✅ 请求/响应字段描述
- ✅ API 摘要信息

---

## v0.2.0 (2026-04-15)

### ✨ 新增功能

#### 认证系统
- ✅ JWT 用户注册/登录
- ✅ Token 存储 (localStorage)
- ✅ 自动鉴权中间件
- ✅ 401 自动跳转登录

#### 对话管理
- ✅ 对话持久化到 PostgreSQL
- ✅ 对话列表侧边栏
- ✅ 历史对话加载
- ✅ 对话删除功能
- ✅ 新对话创建

#### 文档管理
- ✅ 文件上传进度条
- ✅ 批量上传支持 (多文件选择)
- ✅ 文档搜索/筛选
- ✅ 上传状态轮询
- ✅ Celery 任务状态查询 API

#### 导出功能
- ✅ Markdown 格式导出
- ✅ JSON 格式导出
- ✅ 纯文本格式导出

#### UI 增强
- ✅ Markdown 渲染 (代码高亮、表格、列表)
- ✅ 登录/注册页面
- ✅ 统一侧边栏组件
- ✅ 用户信息显示和登出

### 🐛 Bug 修复

- ✅ 修复流式响应引用错误
- ✅ 修复 CORS 安全配置 (限制来源)
- ✅ 文档删除同步清理向量库
- ✅ RAG 服务单例模式修复

### 🔧 技术改进

- ✅ 全局异常处理中间件
- ✅ Axios HTTP 客户端封装
- ✅ 请求/响应拦截器
- ✅ API 服务层封装
- ✅ requirements.txt 生成

---

## v0.1.0 (2026-04-15)

### 初始版本

#### 基础架构
- ✅ Next.js 14 前端框架
- ✅ FastAPI 后端框架
- ✅ Docker Compose 编排
- ✅ PostgreSQL + Redis + Qdrant

#### 核心功能
- ✅ RAG 问答 Pipeline
- ✅ 文档解析 (PDF/DOCX/TXT)
- ✅ 向量存储与检索
- ✅ Ollama LLM 集成

#### 页面
- ✅ 首页 (Hero Section)
- ✅ 问答页面
- ✅ 知识库管理
- ✅ 用户画像

---

## 📊 项目统计

| 类别 | 数量 |
|------|------|
| 后端 API 端点 | 20+ |
| 前端页面 | 6 |
| React 组件 | 10+ |
| Python 服务模块 | 12 |
| 数据模型 | 4 |
| Docker 服务 | 8 |
| WebSocket 端点 | 2 |

---

*最后更新: 2026-04-17*
