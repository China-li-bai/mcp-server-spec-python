# MCP 客户端配置指南

## 🔧 在代码编辑器中配置 MCP 服务器

### 1. 前置要求

- 确保已安装最新版 MCP 插件或 SDK
- Python 3.8+ 环境
- 网络连接（用于远程服务器）

### 2. 配置步骤

#### 2.1 本地服务器配置

**方式一：通过配置文件**

创建 `mcp-config.json`：

```json
{
  "mcpServers": {
    "spec-driven-development": {
      "command": "python",
      "args": ["-m", "mcp_server_spec.main", "--transport", "stdio"],
      "env": {
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**方式二：通过环境变量**

```bash
export MCP_SERVER_ENDPOINT="stdio://python -m mcp_server_spec.main"
export MCP_SERVER_NAME="spec-driven-development"
export MCP_LOG_LEVEL="INFO"
```

#### 2.2 远程服务器配置

**HTTP 流传输配置：**

```json
{
  "mcpServers": {
    "spec-driven-development-remote": {
      "url": "http://localhost:3001",
      "transport": "http-stream",
      "headers": {
        "Authorization": "Bearer your-token-here",
        "Content-Type": "application/json"
      },
      "timeout": 30000,
      "retries": 3
    }
  }
}
```

**SSE 传输配置：**

```json
{
  "mcpServers": {
    "spec-driven-development-sse": {
      "url": "http://localhost:3001",
      "transport": "sse",
      "reconnect": true,
      "heartbeat": 30000
    }
  }
}
```

### 3. TLS 证书验证配置

#### 3.1 生产环境 HTTPS 配置

```json
{
  "mcpServers": {
    "spec-driven-development-secure": {
      "url": "https://your-domain.com:3001",
      "transport": "http-stream",
      "tls": {
        "verify": true,
        "ca": "/path/to/ca-cert.pem",
        "cert": "/path/to/client-cert.pem",
        "key": "/path/to/client-key.pem"
      }
    }
  }
}
```

#### 3.2 开发环境配置（跳过证书验证）

```json
{
  "mcpServers": {
    "spec-driven-development-dev": {
      "url": "https://localhost:3001",
      "transport": "http-stream",
      "tls": {
        "verify": false,
        "allowInsecure": true
      }
    }
  }
}
```

### 4. 持久化连接和心跳机制

#### 4.1 连接池配置

```json
{
  "connectionPool": {
    "maxConnections": 10,
    "keepAlive": true,
    "keepAliveTimeout": 60000,
    "maxIdleTime": 300000
  },
  "heartbeat": {
    "enabled": true,
    "interval": 30000,
    "timeout": 5000,
    "maxFailures": 3
  }
}
```

#### 4.2 重连策略

```json
{
  "reconnection": {
    "enabled": true,
    "maxAttempts": 5,
    "backoff": {
      "type": "exponential",
      "initialDelay": 1000,
      "maxDelay": 30000,
      "multiplier": 2
    }
  }
}
```

### 5. 协议版本配置

确保使用 MCP 协议 v2.1+：

```json
{
  "protocol": {
    "version": "2.1",
    "features": {
      "streaming": true,
      "tools": true,
      "prompts": true,
      "resources": true
    }
  }
}
```

### 6. 完整配置示例

```json
{
  "mcpServers": {
    "spec-driven-development": {
      "url": "http://localhost:3001",
      "transport": "http-stream",
      "protocol": {
        "version": "2.1"
      },
      "connection": {
        "timeout": 30000,
        "retries": 3,
        "keepAlive": true
      },
      "heartbeat": {
        "enabled": true,
        "interval": 30000,
        "timeout": 5000
      },
      "tls": {
        "verify": true
      },
      "headers": {
        "User-Agent": "MCP-Client/1.0",
        "Accept": "application/json"
      }
    }
  },
  "logging": {
    "level": "INFO",
    "file": "mcp-client.log"
  }
}
```

## 🚀 启动和使用

### 1. 启动服务器

```bash
# 本地 stdio 模式
python -m mcp_server_spec.main --transport stdio

# HTTP 流模式
python -m mcp_server_spec.main --transport http-stream --host 0.0.0.0 --port 3001

# SSE 模式
python -m mcp_server_spec.main --transport sse --host 0.0.0.0 --port 3001
```

### 2. 验证连接

```bash
# 健康检查
curl http://localhost:3001/health

# 检查协议版本
curl -H "Accept: application/json" http://localhost:3001/info
```

### 3. 测试提示功能

```bash
# 列出可用提示
curl http://localhost:3001/prompts

# 生成需求文档
curl -X POST http://localhost:3001/prompts/generate-requirements \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2.1" \
  -d '{"arguments": {"requirements": "一个简单的待办事项应用"}}'
```

## 🔍 故障排查

### 1. 常见问题

#### 连接失败
- 检查服务器是否正在运行
- 验证端口是否被占用
- 检查防火墙设置

#### 协议版本不匹配
- 确保客户端和服务器都支持 MCP v2.1+
- 检查响应头中的 `MCP-Protocol-Version`

#### 认证失败
- 验证 API 密钥或令牌
- 检查 TLS 证书配置

### 2. 调试模式

启用详细日志：

```bash
python -m mcp_server_spec.main --transport http-stream --log-level DEBUG
```

### 3. 监控和指标

服务器提供以下监控端点：

- `/health` - 健康状态
- `/metrics` - 性能指标
- `/status` - 服务状态

## 📚 API 参考

### 协议头部

所有请求必须包含以下头部：

```
MCP-Protocol-Version: 2.1
Content-Type: application/json
Accept: application/json
```

### 响应格式

成功响应：
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "content": "响应内容"
  }
}
```

错误响应：
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": -32000,
    "message": "错误描述",
    "data": {}
  }
}
```

## 🔐 安全最佳实践

1. **使用 HTTPS** - 生产环境必须使用 TLS 加密
2. **验证证书** - 不要跳过 TLS 证书验证
3. **限制访问** - 使用防火墙限制访问
4. **定期更新** - 保持 MCP SDK 和服务器版本最新
5. **监控日志** - 定期检查访问日志和错误日志

## 📞 技术支持

如遇问题，请按以下顺序排查：

1. 查看服务器日志
2. 检查网络连接
3. 验证配置文件
4. 测试基本 API 调用
5. 查阅官方文档
6. 提交 Issue 报告