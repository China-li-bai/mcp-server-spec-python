.PHONY: help install install-dev test lint format clean build publish run-stdio run-http run-sse demo

# 默认目标
help:
	@echo "可用命令:"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  lint         - 运行代码检查"
	@echo "  format       - 格式化代码"
	@echo "  clean        - 清理构建文件"
	@echo "  build        - 构建项目"
	@echo "  publish      - 发布到 PyPI"
	@echo "  run-stdio    - 使用 stdio 传输运行服务器"
	@echo "  run-http     - 使用 HTTP 流传输运行服务器"
	@echo "  run-sse      - 使用 SSE 传输运行服务器"
	@echo "  demo         - 运行使用示例"

# 安装项目依赖
install:
	pip install -e .

# 安装开发依赖
install-dev:
	pip install -e ".[dev]"

# 运行测试
test:
	pytest tests/ -v --cov=src/mcp_server_spec --cov-report=html --cov-report=term

# 运行代码检查
lint:
	ruff check src/ tests/ examples/
	mypy src/mcp_server_spec

# 格式化代码
format:
	black src/ tests/ examples/
	isort src/ tests/ examples/
	ruff check --fix src/ tests/ examples/

# 清理构建文件
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 构建项目
build: clean
	python -m build

# 发布到 PyPI
publish: build
	python -m twine upload dist/*

# 使用 stdio 传输运行服务器
run-stdio:
	python -m mcp_server_spec.main --transport stdio

# 使用 HTTP 流传输运行服务器
run-http:
	python -m mcp_server_spec.main --transport http-stream --host 0.0.0.0 --port 3001

# 使用 SSE 传输运行服务器
run-sse:
	python -m mcp_server_spec.main --transport sse --host 0.0.0.0 --port 3001

# 运行使用示例
demo:
	python examples/basic_usage.py

# 开发模式运行（自动重载）
dev-http:
	uvicorn mcp_server_spec.http_stream:app --reload --host 0.0.0.0 --port 3001

# 检查项目结构
check-structure:
	@echo "项目结构:"
	@find . -name "*.py" -not -path "./build/*" -not -path "./dist/*" -not -path "./.pytest_cache/*" | head -20

# 安装预提交钩子
install-hooks:
	pre-commit install

# 运行预提交检查
pre-commit:
	pre-commit run --all-files