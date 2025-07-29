"""
增强的 HTTP 流处理模块 - 支持协议版本检查、TLS 和连接管理
"""

import asyncio
import json
import logging
import ssl
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

from .connection_manager import connection_manager
from .server import SpecDrivenMCPServer

logger = logging.getLogger(__name__)


class EnhancedHTTPStreamServer:
    """增强的 HTTP 流服务器"""
    
    def __init__(self, mcp_server: SpecDrivenMCPServer):
        """
        初始化 HTTP 流服务器
        
        Args:
            mcp_server: MCP 服务器实例
        """
        self.mcp_server = mcp_server
        self.app = FastAPI(
            title="Spec-Driven Development MCP Server",
            description="基于 MCP 协议的规范驱动开发服务器",
            version="0.1.0"
        )
        
        # 添加 CORS 中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
        
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.middleware("http")
        async def protocol_version_middleware(request: Request, call_next):
            """协议版本检查中间件"""
            # 检查协议版本头部
            protocol_version = request.headers.get("MCP-Protocol-Version")
            
            if protocol_version and not self.mcp_server.validate_protocol_version(protocol_version):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": -32000,
                            "message": f"不支持的协议版本: {protocol_version}",
                            "data": {
                                "supported_versions": self.mcp_server.supported_protocol_versions
                            }
                        }
                    },
                    headers={"MCP-Protocol-Version": self.mcp_server.default_protocol_version}
                )
            
            response = await call_next(request)
            
            # 添加协议版本头部到响应
            response.headers["MCP-Protocol-Version"] = protocol_version or self.mcp_server.default_protocol_version
            
            return response
            
        @self.app.get("/health")
        async def health_check():
            """健康检查端点"""
            stats = connection_manager.get_connection_stats()
            return {
                "status": "healthy",
                "server": {
                    "name": self.mcp_server.server_info.name,
                    "version": self.mcp_server.server_info.version,
                    "protocol_versions": self.mcp_server.supported_protocol_versions
                },
                "connections": stats,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        @self.app.get("/info")
        async def server_info():
            """服务器信息端点"""
            return {
                "name": self.mcp_server.server_info.name,
                "version": self.mcp_server.server_info.version,
                "description": self.mcp_server.server_info.description,
                "protocol_versions": self.mcp_server.supported_protocol_versions,
                "features": {
                    "streaming": True,
                    "tools": True,
                    "prompts": True,
                    "resources": True,
                    "heartbeat": True
                }
            }
            
        @self.app.post("/connect")
        async def connect_client(
            request: Request,
            mcp_protocol_version: Optional[str] = Header(None, alias="MCP-Protocol-Version")
        ):
            """客户端连接端点"""
            try:
                body = await request.json()
                client_info = body.get("client_info", {})
                client_info["protocol_version"] = mcp_protocol_version or self.mcp_server.default_protocol_version
                client_info["user_agent"] = request.headers.get("User-Agent")
                client_info["remote_addr"] = request.client.host if request.client else "unknown"
                
                connection_id = await self.mcp_server.handle_connection(client_info)
                
                return {
                    "connection_id": connection_id,
                    "protocol_version": client_info["protocol_version"],
                    "server_info": {
                        "name": self.mcp_server.server_info.name,
                        "version": self.mcp_server.server_info.version
                    }
                }
                
            except Exception as e:
                logger.error(f"连接失败: {e}")
                raise HTTPException(status_code=400, detail=str(e))
                
        @self.app.post("/heartbeat/{connection_id}")
        async def heartbeat(connection_id: str):
            """心跳端点"""
            success = await connection_manager.heartbeat(connection_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="连接不存在")
                
            return {"status": "ok", "timestamp": asyncio.get_event_loop().time()}
            
        @self.app.delete("/disconnect/{connection_id}")
        async def disconnect_client(connection_id: str):
            """断开连接端点"""
            await connection_manager.disconnect(connection_id)
            return {"status": "disconnected"}
            
        @self.app.get("/connections")
        async def list_connections():
            """列出活跃连接"""
            connections = connection_manager.get_active_connections()
            return {
                "connections": [
                    {
                        "id": conn.id,
                        "protocol_version": conn.protocol_version,
                        "created_at": conn.created_at,
                        "last_heartbeat": conn.last_heartbeat,
                        "client_info": conn.client_info
                    }
                    for conn in connections.values()
                ],
                "total": len(connections)
            }
            
        @self.app.get("/prompts")
        async def list_prompts():
            """列出所有可用提示"""
            try:
                prompts = await self.mcp_server.mcp.list_prompts()
                return {
                    "prompts": [
                        {
                            "name": prompt.name,
                            "description": prompt.description,
                            "arguments": prompt.arguments
                        }
                        for prompt in prompts
                    ]
                }
            except Exception as e:
                logger.error(f"列出提示失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/prompts/{prompt_name}")
        async def execute_prompt(
            prompt_name: str,
            request: Request,
            connection_id: Optional[str] = Header(None, alias="X-Connection-ID")
        ):
            """执行提示"""
            try:
                body = await request.json()
                arguments = body.get("arguments", {})
                
                # 验证连接（如果提供了连接ID）
                if connection_id:
                    connection = connection_manager.get_connection(connection_id)
                    if not connection:
                        raise HTTPException(status_code=404, detail="连接不存在")
                
                result = await self.mcp_server.mcp.get_prompt(prompt_name, arguments)
                
                return {
                    "result": {
                        "messages": [
                            {
                                "role": msg.role,
                                "content": msg.content.text if hasattr(msg.content, 'text') else str(msg.content)
                            }
                            for msg in result.messages
                        ]
                    }
                }
                
            except Exception as e:
                logger.error(f"执行提示失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/tools")
        async def list_tools():
            """列出所有可用工具"""
            try:
                tools = await self.mcp_server.mcp.list_tools()
                return {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in tools
                    ]
                }
            except Exception as e:
                logger.error(f"列出工具失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/tools/{tool_name}")
        async def execute_tool(
            tool_name: str,
            request: Request,
            connection_id: Optional[str] = Header(None, alias="X-Connection-ID")
        ):
            """执行工具"""
            try:
                body = await request.json()
                arguments = body.get("arguments", {})
                
                # 验证连接（如果提供了连接ID）
                if connection_id:
                    connection = connection_manager.get_connection(connection_id)
                    if not connection:
                        raise HTTPException(status_code=404, detail="连接不存在")
                
                result = await self.mcp_server.mcp.call_tool(tool_name, arguments)
                
                return {
                    "result": {
                        "content": [
                            {
                                "type": content.type,
                                "text": content.text if hasattr(content, 'text') else str(content)
                            }
                            for content in result.content
                        ],
                        "isError": getattr(result, 'isError', False)
                    }
                }
                
            except Exception as e:
                logger.error(f"执行工具失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/metrics")
        async def get_metrics():
            """获取服务器指标"""
            stats = connection_manager.get_connection_stats()
            return {
                "server": {
                    "uptime": asyncio.get_event_loop().time(),
                    "version": self.mcp_server.server_info.version
                },
                "connections": stats,
                "protocol": {
                    "supported_versions": self.mcp_server.supported_protocol_versions,
                    "default_version": self.mcp_server.default_protocol_version
                }
            }
            
    async def run(self, host: str = "localhost", port: int = 3001, 
                  ssl_keyfile: Optional[str] = None, 
                  ssl_certfile: Optional[str] = None):
        """
        运行 HTTP 服务器
        
        Args:
            host: 主机地址
            port: 端口号
            ssl_keyfile: SSL 私钥文件路径
            ssl_certfile: SSL 证书文件路径
        """
        # 初始化 MCP 服务器
        await self.mcp_server.initialize()
        
        # 配置 SSL
        ssl_context = None
        if ssl_keyfile and ssl_certfile:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(ssl_certfile, ssl_keyfile)
            logger.info(f"启用 HTTPS，证书: {ssl_certfile}")
        
        # 配置 uvicorn
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        
        try:
            protocol = "https" if ssl_context else "http"
            logger.info(f"启动 MCP HTTP 流服务器: {protocol}://{host}:{port}")
            await server.serve()
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务器...")
        finally:
            await self.mcp_server.shutdown()


def create_enhanced_http_stream_server(mcp_server: SpecDrivenMCPServer) -> EnhancedHTTPStreamServer:
    """创建增强的 HTTP 流服务器"""
    return EnhancedHTTPStreamServer(mcp_server)