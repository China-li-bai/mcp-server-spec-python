# 开发指南

本文档提供了 Spec-Driven Development MCP Server (Python) 的开发指南。

## 项目结构

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
│   ├── __init__.py
│   └── test_server.py
├── examples/                     # 使用示例
│   └── basic_usage.py
├── pyproject.toml                # 项目配置
├── README.md                     # 项目说明
├── DEVELOPMENT.md                # 开发指南
├── LICENSE                       # 许可证
├── Makefile                      # 构建脚本
└── .gitignore                    # Git 忽略文件
```

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd mcp-server-spec-python
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
# 安装项目依赖
make install

# 或安装开发依赖
make install-dev
```

## 开发工作流

### 1. 代码格式化

在提交代码前，请确保代码格式正确：

```bash
make format
```

### 2. 运行测试

```bash
make test
```

### 3. 代码检查

```bash
make lint
```

### 4. 运行服务器

```bash
# stdio 传输
make run-stdio

# HTTP 流传输
make run-http

# SSE 传输
make run-sse
```

### 5. 运行示例

```bash
make demo
```

## 架构说明

### 核心组件

1. **SpecDrivenMCPServer** (`server.py`)
   - MCP 服务器的主要实现
   - 处理 MCP 协议消息
   - 管理提示和工具

2. **PromptManager** (`prompts.py`)
   - 管理所有提示模板
   - 处理提示请求和响应
   - 支持 EARS 格式需求生成

3. **HTTPStreamServer** (`http_stream.py`)
   - 提供 HTTP 流处理功能
   - 支持实时响应流
   - 基于 FastAPI 实现

4. **数据模型** (`models.py`)
   - 使用 Pydantic 进行数据验证
   - 定义所有输入输出模型

### 传输方式

项目支持三种传输方式：

1. **stdio** - 标准输入输出传输（默认）
2. **sse** - Server-Sent Events 传输
3. **http-stream** - HTTP 流处理传输

## 添加新功能

### 1. 添加新提示

在 `prompts.py` 中的 `PromptManager` 类中：

1. 在 `_initialize_prompts()` 方法中添加新提示定义
2. 实现对应的提示生成方法
3. 在 `handle_prompt_request()` 方法中添加处理逻辑

示例：

```python
def _initialize_prompts(self):
    prompts = {
        # 现有提示...
        "new-prompt": {
            "title": "新提示",
            "description": "新提示的描述",
            "args_schema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "参数描述"}
                },
                "required": ["param"]
            }
        }
    }
    return prompts

def generate_new_prompt(self, param: str) -> PromptResponse:
    """生成新提示"""
    # 实现逻辑
    pass

def handle_prompt_request(self, name: str, arguments: Dict[str, Any]) -> PromptResponse:
    if name == "new-prompt":
        return self.generate_new_prompt(arguments.get("param", ""))
    # 其他处理逻辑...
```

### 2. 添加新的数据模型

在 `models.py` 中使用 Pydantic 定义新模型：

```python
class NewModel(BaseModel):
    """新模型描述"""
    field1: str = Field(..., description="字段1描述")
    field2: Optional[int] = Field(None, description="字段2描述")
```

### 3. 添加新的 HTTP 端点

在 `http_stream.py` 中的 `_setup_routes()` 方法中添加新路由：

```python
@self.app.get("/new-endpoint")
async def new_endpoint():
    """新端点描述"""
    # 实现逻辑
    return {"message": "新端点响应"}
```

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定测试

```bash
pytest tests/test_server.py::TestPromptManager::test_generate_requirements_prompt -v
```

### 测试覆盖率

```bash
pytest tests/ --cov=src/mcp_server_spec --cov-report=html
```

覆盖率报告将生成在 `htmlcov/` 目录中。

## 调试

### 1. 启用调试日志

```bash
python -m mcp_server_spec.main --log-level DEBUG
```

### 2. 使用调试器

在代码中添加断点：

```python
import pdb; pdb.set_trace()
```

### 3. 测试 HTTP 端点

使用 curl 测试 HTTP 端点：

```bash
# 健康检查
curl http://localhost:3001/health

# 列出提示
curl http://localhost:3001/prompts

# 获取特定提示
curl -X POST http://localhost:3001/prompts/generate-requirements \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"requirements": "测试需求"}}'
```

## 部署

### 1. 构建项目

```bash
make build
```

### 2. 发布到 PyPI

```bash
make publish
```

### 3. Docker 部署

创建 Dockerfile：

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 3001
CMD ["python", "-m", "mcp_server_spec.main", "--transport", "http-stream", "--host", "0.0.0.0", "--port", "3001"]
```

构建和运行：

```bash
docker build -t mcp-server-spec-python .
docker run -p 3001:3001 mcp-server-spec-python
```

## 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature/new-feature`
5. 创建 Pull Request

### 代码规范

- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 Ruff 进行代码检查
- 使用 mypy 进行类型检查
- 编写测试覆盖新功能
- 更新文档

## 常见问题

### Q: 如何添加新的传输方式？

A: 在 `main.py` 中添加新的传输处理函数，并在参数解析中添加新选项。

### Q: 如何修改提示模板？

A: 在 `prompts.py` 中的相应方法中修改提示文本。

### Q: 如何处理错误？

A: 使用适当的异常类型，并确保在 HTTP 端点中正确处理和返回错误响应。

## 更多资源

- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastAPI 文档](https://fastapi.tiangolo.com)
- [Pydantic 文档](https://docs.pydantic.dev)