# Setup Guide for MCP Spec-Driven Development Server (Python)

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

### Option 1: Using pip

```bash
# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using uv (recommended for faster installation)

```bash
# Install uv if you haven't already
pip install uv

# Install dependencies with uv
uv pip install -r requirements.txt
```

### Option 3: Using virtual environment (recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Testing Installation

Run the syntax test to verify everything is working:

```bash
python test_syntax.py
```

If successful, you should see:
```
✓ Server module imported successfully
✓ Server created successfully
✓ Server name: spec-driven-development
✓ Server version: 1.0.0

🎉 All syntax tests passed!
```

## Running the Server

### Stdio Transport (for MCP clients like Claude Desktop)

```bash
python src/main.py
```

### HTTP Transport (for web-based clients)

```bash
python src/http_server.py
```

The HTTP server will start on `http://localhost:3088`

## Usage with MCP Inspector

To test the server with MCP Inspector:

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector

# Test stdio transport
npx @modelcontextprotocol/inspector python src/main.py

# Test HTTP transport (start HTTP server first)
npx @modelcontextprotocol/inspector http://localhost:3088/mcp
```

## Available Prompts

1. **generate-requirements**: Generate requirements.md from high-level input
2. **generate-design-from-requirements**: Generate design.md from requirements.md
3. **generate-code-from-design**: Generate implementation code from design.md

## Troubleshooting

### Python not found
- Make sure Python is installed and added to your PATH
- Try using `python3` instead of `python`
- On Windows, you might need to install Python from the Microsoft Store

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the correct directory
- Try using a virtual environment

### Permission errors
- On Windows, try running as administrator
- On macOS/Linux, check file permissions

## Development

For development, install additional dependencies:

```bash
pip install pytest black isort mypy
```

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
isort src/
```

Type checking:
```bash
mypy src/
```