"""
MCP 服务器核心实现

基于 MCP Python SDK 实现的规范驱动开发服务器
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, Sequence

from mcp import FastMCP
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    ListToolsRequest,
    ListToolsResult,
    Prompt,
    PromptMessage,
    TextContent,
    Tool,
)

from .models import PromptRequest, PromptResponse, ServerInfo
from .prompts import PromptManager
from .connection_manager import connection_manager

logger = logging.getLogger(__name__)


class SpecDrivenMCPServer:
    """规范驱动开发 MCP 服务器"""
    
    def __init__(self):
        """初始化服务器"""
        self.prompt_manager = PromptManager()
        self.server_info = ServerInfo(
            name="spec-driven-development",
            version="0.1.0",
            description="规范驱动开发 MCP 服务器"
        )
        
        # 支持的协议版本
        self.supported_protocol_versions = ["2.0", "2.1", "2.2"]
        self.default_protocol_version = "2.1"
        
        # 创建 FastMCP 实例
        self.mcp = FastMCP(self.server_info.name)
        self._setup_handlers()
        
    async def initialize(self):
        """初始化服务器"""
        await connection_manager.start()
        logger.info("MCP 服务器初始化完成")
        
    async def shutdown(self):
        """关闭服务器"""
        await connection_manager.stop()
        logger.info("MCP 服务器已关闭")
        
    def validate_protocol_version(self, version: str) -> bool:
        """验证协议版本"""
        return version in self.supported_protocol_versions
        
    async def handle_connection(self, client_info: Dict[str, Any]) -> str:
        """处理新连接"""
        connection_id = str(uuid.uuid4())
        protocol_version = client_info.get("protocol_version", self.default_protocol_version)
        
        if not self.validate_protocol_version(protocol_version):
            raise ValueError(f"不支持的协议版本: {protocol_version}")
            
        success = await connection_manager.connect(
            connection_id=connection_id,
            protocol_version=protocol_version,
            client_info=client_info
        )
        
        if not success:
            raise RuntimeError("连接建立失败")
            
        return connection_id
        
    def _setup_handlers(self):
        """设置 MCP 处理器"""
        
        @self.mcp.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """列出所有可用的提示"""
            prompts = []
            for name, config in self.prompt_manager.prompts.items():
                prompts.append(Prompt(
                    name=name,
                    description=config["description"],
                    arguments=config.get("args_schema", {}).get("properties", {})
                ))
            return prompts
            
        @self.mcp.get_prompt()
        async def get_prompt(name: str, arguments: Optional[Dict[str, Any]] = None) -> GetPromptResult:
            """获取特定提示"""
            try:
                if arguments is None:
                    arguments = {}
                    
                response = self.prompt_manager.handle_prompt_request(name, arguments)
                
                messages = [
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=response.content
                        )
                    )
                ]
                
                return GetPromptResult(messages=messages)
                
            except Exception as e:
                logger.error(f"处理提示请求时出错: {e}")
                raise
                
        @self.mcp.list_tools()
        async def list_tools() -> List[Tool]:
            """列出所有可用的工具"""
            return [
                Tool(
                    name="create_file",
                    description="创建文件",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"},
                            "content": {"type": "string", "description": "文件内容"}
                        },
                        "required": ["path", "content"]
                    }
                ),
                Tool(
                    name="read_file",
                    description="读取文件",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"}
                        },
                        "required": ["path"]
                    }
                )
            ]
            
        @self.mcp.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """调用工具"""
            try:
                if name == "create_file":
                    return await self._create_file(arguments)
                elif name == "read_file":
                    return await self._read_file(arguments)
                else:
                    raise ValueError(f"未知工具: {name}")
                    
            except Exception as e:
                logger.error(f"调用工具时出错: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"错误: {str(e)}")],
                    isError=True
                )
                
    async def _create_file(self, arguments: Dict[str, Any]) -> CallToolResult:
        """创建文件工具"""
        path = arguments.get("path")
        content = arguments.get("content")
        
        if not path or not content:
            raise ValueError("路径和内容都是必需的")
            
        try:
            import os
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return CallToolResult(
                content=[TextContent(type="text", text=f"文件已创建: {path}")]
            )
            
        except Exception as e:
            raise ValueError(f"创建文件失败: {str(e)}")
            
    async def _read_file(self, arguments: Dict[str, Any]) -> CallToolResult:
        """读取文件工具"""
        path = arguments.get("path")
        
        if not path:
            raise ValueError("文件路径是必需的")
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return CallToolResult(
                content=[TextContent(type="text", text=content)]
            )
            
        except FileNotFoundError:
            raise ValueError(f"文件不存在: {path}")
        except Exception as e:
            raise ValueError(f"读取文件失败: {str(e)}")
    
    async def run_stdio(self):
        """使用 stdio 传输运行服务器"""
        logger.info("启动 MCP 服务器 (stdio 传输)")
        await self.mcp.run()
        
    def get_app(self):
        """获取 FastAPI 应用实例"""
        return self.mcp.create_app()


def create_server() -> SpecDrivenMCPServer:
    """创建服务器实例"""
    return SpecDrivenMCPServer()


async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    server = create_server()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())