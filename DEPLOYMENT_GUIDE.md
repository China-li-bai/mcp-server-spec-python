# 🚀 MCP 服务器部署指南

## 📋 部署前检查清单

### 系统要求
- Python 3.8+
- 2GB+ 内存
- 1GB+ 磁盘空间
- 网络连接

### 依赖检查
```bash
# 检查 Python 版本
python --version

# 检查 pip
pip --version

# 检查网络连接
curl -I https://pypi.org
```

## 🔧 安装和配置

### 1. 克隆项目
```bash
git clone <repository-url>
cd mcp-server-spec-python
```

### 2. 安装依赖
```bash
# 生产环境
pip install -e .

# 开发环境
pip install -e ".[dev]"
```

### 3. 验证安装
```bash
python -m mcp_server_spec.main --version
```

## 🌐 部署模式

### 1. 本地开发模式

**stdio 传输（推荐用于开发）:**
```bash
python -m mcp_server_spec.main --transport stdio
```

**HTTP 流传输（推荐用于测试）:**
```bash
python -m mcp_server_spec.main \
  --transport http-stream \
  --host localhost \
  --port 3001
```

### 2. 生产环境模式

**基础 HTTP 部署:**
```bash
python -m mcp_server_spec.main \
  --transport http-stream \
  --host 0.0.0.0 \
  --port 3001 \
  --log-level INFO
```

**HTTPS 安全部署:**
```bash
python -m mcp_server_spec.main \
  --transport http-stream \
  --host 0.0.0.0 \
  --port 3001 \
  --ssl-keyfile /path/to/server.key \
  --ssl-certfile /path/to/server.crt \
  --log-level INFO
```

### 3. 容器化部署

**创建 Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install -e .

# 暴露端口
EXPOSE 3001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# 启动命令
CMD ["python", "-m", "mcp_server_spec.main", \
     "--transport", "http-stream", \
     "--host", "0.0.0.0", \
     "--port", "3001"]
```

**构建和运行:**
```bash
# 构建镜像
docker build -t mcp-server-spec-python .

# 运行容器
docker run -d \
  --name mcp-server \
  -p 3001:3001 \
  --restart unless-stopped \
  mcp-server-spec-python

# 查看日志
docker logs -f mcp-server
```

### 4. 使用 Docker Compose

**创建 docker-compose.yml:**
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "3001:3001"
    environment:
      - MCP_LOG_LEVEL=INFO
      - MCP_SERVER_HOST=0.0.0.0
      - MCP_SERVER_PORT=3001
    volumes:
      - ./specs:/app/specs
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mcp-server
    restart: unless-stopped
```

**启动服务:**
```bash
docker-compose up -d
```

## 🔐 SSL/TLS 配置

### 1. 生成自签名证书（开发用）
```bash
# 生成私钥
openssl genrsa -out server.key 2048

# 生成证书签名请求
openssl req -new -key server.key -out server.csr

# 生成自签名证书
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

### 2. 使用 Let's Encrypt（生产用）
```bash
# 安装 certbot
sudo apt-get install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 证书路径
# 私钥: /etc/letsencrypt/live/your-domain.com/privkey.pem
# 证书: /etc/letsencrypt/live/your-domain.com/fullchain.pem
```

### 3. Nginx 反向代理配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /health {
        proxy_pass http://localhost:3001/health;
        access_log off;
    }
}
```

## 📊 监控和日志

### 1. 日志配置
```bash
# 设置日志级别
export MCP_LOG_LEVEL=INFO

# 日志文件路径
export MCP_LOG_FILE=/var/log/mcp-server.log

# 启动服务器
python -m mcp_server_spec.main \
  --transport http-stream \
  --log-level INFO \
  2>&1 | tee /var/log/mcp-server.log
```

### 2. 系统服务配置

**创建 systemd 服务文件 `/etc/systemd/system/mcp-server.service`:**
```ini
[Unit]
Description=MCP Spec-Driven Development Server
After=network.target

[Service]
Type=simple
User=mcp
Group=mcp
WorkingDirectory=/opt/mcp-server-spec-python
Environment=PATH=/opt/mcp-server-spec-python/venv/bin
ExecStart=/opt/mcp-server-spec-python/venv/bin/python -m mcp_server_spec.main --transport http-stream --host 0.0.0.0 --port 3001
Restart=always
RestartSec=10

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcp-server

# 安全配置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/mcp-server-spec-python/specs /opt/mcp-server-spec-python/logs

[Install]
WantedBy=multi-user.target
```

**启用和启动服务:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
sudo systemctl status mcp-server
```

### 3. 监控脚本

**创建健康检查脚本 `health_check.sh`:**
```bash
#!/bin/bash

URL="http://localhost:3001/health"
TIMEOUT=10

response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "$URL")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✓ MCP 服务器健康"
    exit 0
else
    echo "✗ MCP 服务器异常 (HTTP: $http_code)"
    exit 1
fi
```

**设置定时检查:**
```bash
# 添加到 crontab
*/5 * * * * /path/to/health_check.sh >> /var/log/mcp-health.log 2>&1
```

## 🔧 性能优化

### 1. 系统级优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化网络参数
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p
```

### 2. 应用级优化
```bash
# 使用多进程部署
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:3001 \
  --access-logfile /var/log/mcp-access.log \
  --error-logfile /var/log/mcp-error.log \
  mcp_server_spec.main:app
```

## 🧪 部署验证

### 1. 运行测试脚本
```bash
python test_mcp_server.py
```

### 2. 手动验证
```bash
# 健康检查
curl http://localhost:3001/health

# 服务器信息
curl http://localhost:3001/info

# 协议版本检查
curl -H "MCP-Protocol-Version: 2.1" http://localhost:3001/health
```

### 3. 负载测试
```bash
# 安装 Apache Bench
sudo apt-get install apache2-utils

# 运行负载测试
ab -n 1000 -c 10 http://localhost:3001/health
```

## 🚨 故障排查

### 常见问题

1. **端口被占用**
   ```bash
   sudo lsof -i :3001
   sudo netstat -tulpn | grep 3001
   ```

2. **权限问题**
   ```bash
   sudo chown -R mcp:mcp /opt/mcp-server-spec-python
   sudo chmod +x /opt/mcp-server-spec-python/venv/bin/python
   ```

3. **SSL 证书问题**
   ```bash
   openssl x509 -in server.crt -text -noout
   openssl rsa -in server.key -check
   ```

4. **内存不足**
   ```bash
   free -h
   top -p $(pgrep -f mcp_server_spec)
   ```

### 日志分析
```bash
# 查看系统日志
sudo journalctl -u mcp-server -f

# 查看应用日志
tail -f /var/log/mcp-server.log

# 错误统计
grep -c "ERROR" /var/log/mcp-server.log
```

## 📈 扩展部署

### 1. 负载均衡
使用 Nginx 或 HAProxy 进行负载均衡：

```nginx
upstream mcp_backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    listen 80;
    location / {
        proxy_pass http://mcp_backend;
    }
}
```

### 2. 高可用部署
- 使用 Docker Swarm 或 Kubernetes
- 配置健康检查和自动重启
- 实现数据持久化和备份

### 3. 监控集成
- Prometheus + Grafana
- ELK Stack (Elasticsearch + Logstash + Kibana)
- 自定义监控指标

## 🎯 最佳实践

1. **安全性**
   - 使用 HTTPS
   - 定期更新依赖
   - 限制访问权限
   - 启用防火墙

2. **可靠性**
   - 实现健康检查
   - 配置自动重启
   - 设置监控告警
   - 定期备份数据

3. **性能**
   - 使用反向代理
   - 启用缓存
   - 优化数据库查询
   - 监控资源使用

4. **维护性**
   - 结构化日志
   - 版本控制
   - 自动化部署
   - 文档更新

---

部署完成后，您的 MCP 服务器将能够：
- 处理规范驱动开发工作流
- 支持多种传输协议
- 提供安全的 HTTPS 连接
- 实现连接管理和心跳机制
- 遵循 MCP 协议 v2.1+ 规范

如有问题，请参考故障排查部分或提交 Issue。