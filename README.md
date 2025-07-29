# Spec-Driven Development MCP Server (Python)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于 Model Context Protocol (MCP) 的规范驱动开发服务器的 Python 实现，通过结构化提示促进从需求到设计再到代码的系统化开发工作流。

## 🎯 项目目标

本 MCP 服务器使开发者能够遵循结构化的规范驱动开发方法，通过提供引导性提示来完成：

1. **需求生成** - 使用 EARS (Easy Approach to Requirements Syntax) 格式创建详细的需求文档
2. **设计生成** - 基于需求生成设计文档
3. **代码生成** - 基于设计文档生成实现代码

## ✨ 特性

- **结构化工作流**: 遵循清晰的 **需求** → **设计** → **代码** 进展路径
- **EARS 格式支持**: 使用行业标准的 EARS 格式进行需求文档编写
- **MCP 协议**: 与 MCP 兼容的工具和环境无缝集成
- **多种传输方式**: 支持 stdio、HTTP 流和 SSE 传输
- **Python 实现**: 基于现代 Python 技术栈构建

## 🚀 快速开始

### 前置要求

- Python 3.8+
- pip 或 poetry

### 安装

#### 从源码安装

```bash
git clone <repository-url>
cd mcp-server-spec-python
pip install -e .
```

#### 开发安装

```bash
pip install -e ".[dev]"
```

### 运行服务器

#### 1. stdio 传输（默认）

```bash
python -m mcp_server_spec.main --transport stdio
```

#### 2. HTTP 流传输

```bash
python -m mcp_server_spec.main --transport http-stream --host 0.0.0.0 --port 3001
```

#### 3. SSE 传输

```bash
python -m mcp_server_spec.main --transport sse --host 0.0.0.0 --port 3001
```

### 使用 Makefile

```bash
# 安装依赖
make install

# 运行 stdio 服务器
make run-stdio

# 运行 HTTP 流服务器
make run-http

# 运行 SSE 服务器
make run-sse

# 运行测试
make test

# 代码格式化
make format
```

## 📋 可用提示

### 1. 生成需求文档
- **名称**: `generate-requirements`
- **描述**: 使用 EARS 格式生成 requirements.md
- **输入**: 应用程序的高级需求。例如：'一个带有任务创建、完成跟踪和本地存储持久化的 Vue.js 待办事项应用程序'
- **输出**: `specs/requirements.md` 中的结构化需求文档

### 2. 从需求生成设计
- **名称**: `generate-design-from-requirements`
- **描述**: 从 requirements.md 生成 design.md
- **输入**: 从 `specs/requirements.md` 读取
- **输出**: `specs/design.md` 中的设计文档

### 3. 从设计生成代码
- **名称**: `generate-code-from-design`
- **描述**: 从 design.md 生成代码
- **输入**: 从 `specs/design.md` 读取
- **输出**: 根目录中的实现代码

## 📖 工作流示例

1. **从需求开始**: 使用 `generate-requirements` 提示和您的初始需求文本
2. **创建设计**: 使用 `generate-design-from-requirements` 基于您的需求创建设计文档
3. **生成代码**: 使用 `generate-code-from-design` 从您的设计生成实现代码

这创建了从需求到设计再到实现的可追溯路径，确保开发过程的一致性和完整性。

## 🏗️ 项目结构

```
mcp-server-spec-python/
├── src/mcp_server_spec/          # 主要源代码
│   ├── __init__.py               # 包初始化
│   ├── main.py                   # 应用入口点
│   ├── server.py                 # MCP 服务器核心逻辑
│   ├── http_stream.py            # HTTP 流处理模块
│   ├── models.py                 # 数据模型定义
│   └── prompts.py                # 提示模板管理
├── tests/                        # 测试文件
├── examples/                     # 使用示例
├── pyproject.toml                # 项目配置
├── README.md                     # 项目说明
├── DEVELOPMENT.md                # 开发指南
└── Makefile                      # 构建脚本
```

## 🔧 配置

### 环境变量

- `MCP_SERVER_HOST`: 服务器主机 (默认: localhost)
- `MCP_SERVER_PORT`: 服务器端口 (默认: 3001)
- `MCP_LOG_LEVEL`: 日志级别 (默认: INFO)
- `MCP_TRANSPORT`: 传输方式 (默认: stdio)

### 配置文件

可以通过命令行参数或环境变量进行配置：

```bash
python -m mcp_server_spec.main \
  --transport http-stream \
  --host 0.0.0.0 \
  --port 3001 \
  --log-level DEBUG
```

## 🧪 测试

### 运行所有测试

```bash
make test
```

### 运行特定测试

```bash
pytest tests/test_server.py -v
```

### 测试覆盖率

```bash
pytest tests/ --cov=src/mcp_server_spec --cov-report=html
```

## 🔌 API 端点 (HTTP 传输)

当使用 HTTP 流传输时，服务器提供以下端点：

- `GET /health` - 健康检查
- `GET /prompts` - 列出所有可用提示
- `POST /prompts/{prompt_name}` - 执行特定提示
- `GET /tools` - 列出所有可用工具
- `POST /tools/{tool_name}` - 执行特定工具

### 示例请求

```bash
# 健康检查
curl http://localhost:3001/health

# 列出提示
curl http://localhost:3001/prompts

# 生成需求文档
curl -X POST http://localhost:3001/prompts/generate-requirements \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"requirements": "一个简单的待办事项应用"}}'
```

## 🐳 Docker 支持

### 构建镜像

```bash
docker build -t mcp-server-spec-python .
```

### 运行容器

```bash
docker run -p 3001:3001 mcp-server-spec-python
```

## 🤝 贡献

欢迎贡献！请查看 [DEVELOPMENT.md](DEVELOPMENT.md) 了解开发指南。

### 开发工作流

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送到分支: `git push origin feature/amazing-feature`
5. 打开 Pull Request

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Ruff 进行代码检查
- 使用 MyPy 进行类型检查
- 编写测试覆盖新功能

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [原始 TypeScript 版本](https://github.com/formulahendry/mcp-server-spec-driven-development)

## 📞 支持

如果您遇到任何问题或有疑问，请：

1. 查看 [DEVELOPMENT.md](DEVELOPMENT.md) 中的常见问题
2. 搜索现有的 [Issues](https://github.com/formulahendry/mcp-server-spec-driven-development-python/issues)
3. 创建新的 Issue 描述您的问题

## 🎉 致谢

- 感谢 [MCP 团队](https://modelcontextprotocol.io) 提供优秀的协议和 SDK
- 感谢原始 TypeScript 版本的贡献者们
- 感谢所有为本项目做出贡献的开发者们