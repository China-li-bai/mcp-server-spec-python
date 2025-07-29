# Spec-Driven Development MCP Server (Python)

A Python implementation of the Spec-Driven Development MCP Server using the official MCP Python SDK with FastMCP.

## 🎯 Purpose

This MCP server enables developers to follow a structured spec-driven development approach by providing prompts that guide you through:

1. **Requirements Generation** - Create detailed requirements documents using the EARS (Easy Approach to Requirements Syntax) format
2. **Design Generation** - Generate design documents based on requirements
3. **Code Generation** - Generate implementation code based on design documents

## ✨ Features

- **Structured Workflow**: Follows a clear progression from **requirements** → **design** → **code**
- **EARS Format Support**: Uses industry-standard EARS format for requirements documentation
- **MCP Protocol**: Integrates seamlessly with MCP-compatible tools and environments
- **Multiple Transports**: Supports both stdio and HTTP transports
- **FastMCP**: Built with the modern FastMCP framework for clean, Pythonic code

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- uv (recommended) or pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-server-spec-python

# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Usage

#### Stdio Transport (for MCP clients)
```bash
# Using uv
uv run python src/main.py

# Or directly
python src/main.py
```

#### HTTP Transport (for web integration)
```bash
# Using uv
uv run python src/http_server.py

# Or directly
python src/http_server.py
```

The HTTP server will start on port 3088 by default.

## 📋 Available Prompts

### 1. Generate Requirements Document
- **Name**: `generate-requirements`
- **Description**: Generate requirements.md using EARS format
- **Input**: High-level requirements of the application
- **Output**: Structured requirements document in `specs/requirements.md`

### 2. Generate Design from Requirements
- **Name**: `generate-design-from-requirements`
- **Description**: Generate design.md from requirements.md
- **Input**: Reads from `specs/requirements.md`
- **Output**: Design document in `specs/design.md`

### 3. Generate Code from Design
- **Name**: `generate-code-from-design`
- **Description**: Generate code from design.md
- **Input**: Reads from `specs/design.md`
- **Output**: Implementation code in the root folder

## 📖 Workflow Example

1. **Start with Requirements**: Use the `generate-requirements` prompt with your initial requirements text
2. **Create Design**: Use `generate-design-from-requirements` to create a design document based on your requirements
3. **Generate Code**: Use `generate-code-from-design` to generate implementation code from your design

This creates a traceable path from requirements through design to implementation, ensuring consistency and completeness in your development process.

## 🛠️ Development

### Project Structure

```
mcp-server-spec-python/
├── src/
│   ├── __init__.py
│   ├── main.py              # Stdio transport entry point
│   ├── http_server.py       # HTTP transport entry point
│   └── server.py            # Core MCP server implementation
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Testing

Use the MCP Inspector for testing:

```bash
uv run mcp-inspector src/main.py
```
### 🔧 客戶端配置示例 對於支持HTTP傳輸的MCP客戶端：
```json
{
  "transport": "http",
  "url": "http://192.227.177.133:3088/mcp",
  "method": "POST"
}
### 🔧 對於Claude Desktop等客戶端
```json
{
  "mcpServers": {
    "spec-driven-dev": {
      "transport": "http",
      "url": "http://192.227.177.133:3088/mcp"
    }
  }
}
```


## 📄 License

MIT License