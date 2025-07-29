"""
HTTP 流处理模块

提供基于 FastAPI 的 HTTP 流处理功能，支持实时响应流。
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

from .models import HealthCheckResponse, ErrorResponse
from .server import SpecDrivenMCPServer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPStreamServer:
    """HTTP 流服务器"""
    
    def __init__(self, mcp_server: SpecDrivenMCPServer):
        """初始化 HTTP 流服务器"""
        self.mcp_server = mcp_server
        self.app = FastAPI(
            title="Spec-Driven Development MCP Server",
            description="HTTP 流接口用于规范驱动开发 MCP 服务器",
            version="0.1.0"
        )
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """设置中间件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.get("/health")
        async def health_check() -> HealthCheckResponse:
            """健康检查端点"""
            return HealthCheckResponse(
                status="healthy",
                version=self.mcp_server.server_info.version,
                timestamp=datetime.now().isoformat()
            )
        
        @self.app.get("/prompts")
        async def list_prompts():
            """列出所有可用的提示"""
            try:
                prompt_definitions = self.mcp_server.prompt_manager.get_prompt_definitions()
                prompts = []
                
                for name, definition in prompt_definitions.items():
                    prompts.append({
                        "name": name,
                        "title": definition["title"],
                        "description": definition["description"],
                        "args_schema": definition.get("args_schema", {})
                    })
                
                return {"prompts": prompts}
                
            except Exception as e:
                logger.error(f"列出提示时出错: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/prompts/{prompt_name}")
        async def get_prompt(prompt_name: str, request: Request):
            """获取特定提示的内容"""
            try:
                body = await request.json() if request.headers.get("content-type") == "application/json" else {}
                arguments = body.get("arguments", {})
                
                logger.info(f"处理提示请求: {prompt_name}, 参数: {arguments}")
                
                # 验证提示是否存在
                prompt_def = self.mcp_server.prompt_manager.get_prompt_definition(prompt_name)
                if not prompt_def:
                    raise HTTPException(status_code=404, detail=f"未找到提示: {prompt_name}")
                
                # 生成提示响应
                prompt_response = self.mcp_server.prompt_manager.handle_prompt_request(prompt_name, arguments)
                
                # 转换为 HTTP 响应格式
                response_data = {
                    "description": prompt_def["description"],
                    "messages": []
                }
                
                for msg in prompt_response.messages:
                    response_data["messages"].append({
                        "role": msg.role,
                        "content": msg.content
                    })
                
                return response_data
                
            except ValueError as e:
                logger.error(f"参数验证错误: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"处理提示请求时出错 {prompt_name}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/prompts/{prompt_name}/stream")
        async def get_prompt_stream(prompt_name: str, request: Request):
            """获取特定提示的流式内容"""
            try:
                body = await request.json() if request.headers.get("content-type") == "application/json" else {}
                arguments = body.get("arguments", {})
                
                logger.info(f"处理流式提示请求: {prompt_name}, 参数: {arguments}")
                
                # 验证提示是否存在
                prompt_def = self.mcp_server.prompt_manager.get_prompt_definition(prompt_name)
                if not prompt_def:
                    raise HTTPException(status_code=404, detail=f"未找到提示: {prompt_name}")
                
                async def generate_stream():
                    """生成流式响应"""
                    try:
                        # 发送开始事件
                        yield f"data: {json.dumps({'type': 'start', 'prompt': prompt_name})}\n\n"
                        
                        # 生成提示响应
                        prompt_response = self.mcp_server.prompt_manager.handle_prompt_request(prompt_name, arguments)
                        
                        # 发送提示信息
                        yield f"data: {json.dumps({'type': 'info', 'description': prompt_def['description']})}\n\n"
                        
                        # 逐个发送消息
                        for i, msg in enumerate(prompt_response.messages):
                            message_data = {
                                "type": "message",
                                "index": i,
                                "role": msg.role,
                                "content": msg.content
                            }
                            yield f"data: {json.dumps(message_data)}\n\n"
                            
                            # 模拟流式处理延迟
                            await asyncio.sleep(0.1)
                        
                        # 发送完成事件
                        yield f"data: {json.dumps({'type': 'complete', 'total_messages': len(prompt_response.messages)})}\n\n"
                        
                    except Exception as e:
                        # 发送错误事件
                        error_data = {
                            "type": "error",
                            "error": str(e)
                        }
                        yield f"data: {json.dumps(error_data)}\n\n"
                
                return StreamingResponse(
                    generate_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                    }
                )
                
            except ValueError as e:
                logger.error(f"参数验证错误: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"处理流式提示请求时出错 {prompt_name}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/server/info")
        async def get_server_info():
            """获取服务器信息"""
            return {
                "name": self.mcp_server.server_info.name,
                "version": self.mcp_server.server_info.version,
                "capabilities": ["prompts", "streaming"],
                "transport": "http"
            }
        
        @self.app.exception_handler(404)
        async def not_found_handler(request: Request, exc: HTTPException):
            """404 错误处理器"""
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": 404,
                        "message": "未找到请求的资源",
                        "path": str(request.url.path)
                    }
                }
            )
        
        @self.app.exception_handler(500)
        async def internal_error_handler(request: Request, exc: HTTPException):
            """500 错误处理器"""
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": "内部服务器错误",
                        "detail": str(exc.detail) if hasattr(exc, 'detail') else None
                    }
                }
            )
    
    async def run(self, host: str = "localhost", port: int = 3001):
        """运行 HTTP 流服务器"""
        logger.info(f"启动 HTTP 流服务器在 http://{host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()


def create_http_stream_server(mcp_server: SpecDrivenMCPServer) -> HTTPStreamServer:
    """创建 HTTP 流服务器实例"""
    return HTTPStreamServer(mcp_server)


async def main():
    """主函数 - 运行 HTTP 流服务器"""
    from .server import create_server
    
    # 创建 MCP 服务器
    mcp_server = create_server()
    
    # 创建 HTTP 流服务器
    http_server = create_http_stream_server(mcp_server)
    
    # 运行服务器
    await http_server.run()


if __name__ == "__main__":
    asyncio.run(main())