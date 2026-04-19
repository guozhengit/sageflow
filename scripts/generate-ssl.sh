#!/bin/bash
# 生成自签名 SSL 证书 (仅用于开发环境)
# 生产环境请使用 Let's Encrypt

set -e

SSL_DIR="./nginx/ssl"

echo "🔒 生成自签名 SSL 证书..."

# 创建 SSL 目录
mkdir -p $SSL_DIR

# 生成私钥和证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout $SSL_DIR/server.key \
    -out $SSL_DIR/server.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=SageFlow/OU=Dev/CN=localhost"

# 设置权限
chmod 600 $SSL_DIR/server.key
chmod 644 $SSL_DIR/server.crt

echo "✅ SSL 证书已生成:"
echo "   - 证书: $SSL_DIR/server.crt"
echo "   - 私钥: $SSL_DIR/server.key"
echo ""
echo "⚠️  注意: 这是自签名证书，仅用于开发环境"
echo "   生产环境请使用 Let's Encrypt 或其他 CA 签发的证书"
