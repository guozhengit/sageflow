# SageFlow Kubernetes 部署指南

## 前提条件

- Kubernetes 集群 (1.24+)
- kubectl 命令行工具
- Helm 3 (可选)
- Nginx Ingress Controller
- Cert-Manager (用于 HTTPS)
- 存储类 (StorageClass)

## 快速部署

### 1. 安装 Nginx Ingress Controller

```bash
# 使用 Helm 安装
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

### 2. 安装 Cert-Manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 创建 ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 3. 构建并推送镜像

```bash
# 构建后端镜像
docker build -t sageflow-backend:latest ./backend
docker push your-registry/sageflow-backend:latest

# 构建前端镜像
docker build -t sageflow-frontend:latest ./frontend
docker push your-registry/sageflow-frontend:latest
```

### 4. 修改配置

编辑 `secrets.yaml`，设置安全的密码和密钥：

```bash
# 生成安全的密钥
openssl rand -hex 32

# 编辑 secrets.yaml
vim k8s/secrets.yaml
```

编辑 `ingress.yaml`，修改域名：

```bash
sed -i 's/sageflow.example.com/your-domain.com/g' k8s/ingress.yaml
```

### 5. 部署 SageFlow

```bash
# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 应用配置
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# 部署基础设施
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/qdrant.yaml
kubectl apply -f k8s/ollama.yaml

# 等待基础设施就绪
kubectl wait --for=condition=ready pod -l app=postgres -n sageflow --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n sageflow --timeout=300s
kubectl wait --for=condition=ready pod -l app=qdrant -n sageflow --timeout=300s

# 部署应用
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/celery.yaml

# 部署 Ingress 和 HPA
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/pdb.yaml
```

### 6. 验证部署

```bash
# 检查 Pod 状态
kubectl get pods -n sageflow

# 检查服务状态
kubectl get services -n sageflow

# 检查 Ingress
kubectl get ingress -n sageflow

# 查看日志
kubectl logs -f deployment/backend -n sageflow
```

## 一键部署脚本

```bash
# 部署所有资源
kubectl apply -f k8s/

# 或使用脚本
./scripts/deploy-k8s.sh
```

## 配置说明

### 资源配置

| 组件 | CPU 请求 | CPU 限制 | 内存请求 | 内存限制 |
|------|----------|----------|----------|----------|
| PostgreSQL | 100m | 500m | 256Mi | 1Gi |
| Redis | 50m | 200m | 128Mi | 512Mi |
| Qdrant | 100m | 500m | 256Mi | 2Gi |
| Ollama | 1 | 2 | 2Gi | 4Gi |
| Backend | 250m | 1 | 512Mi | 2Gi |
| Frontend | 100m | 500m | 256Mi | 1Gi |
| Celery | 100m | 500m | 256Mi | 1Gi |

### 自动扩缩容

- Backend: 2-10 副本 (CPU > 70%)
- Frontend: 2-5 副本 (CPU > 70%)
- Celery: 1-5 副本 (CPU > 70%)

## 常见问题

### 1. Ollama 模型未下载

```bash
# 进入 Ollama Pod 下载模型
kubectl exec -it deployment/ollama -n sageflow -- ollama pull qwen2.5:3b
```

### 2. 数据库迁移

```bash
# 进入 Backend Pod 执行迁移
kubectl exec -it deployment/backend -n sageflow -- alembic upgrade head
```

### 3. 查看 Ingress 日志

```bash
kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
```

## 卸载

```bash
# 删除所有资源
kubectl delete -f k8s/

# 或删除命名空间
kubectl delete namespace sageflow
```
