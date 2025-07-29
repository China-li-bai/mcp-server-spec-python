#!/usr/bin/env python3
"""
MCP 客户端配置示例

演示如何配置和连接到 MCP 服务器
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    """MCP 客户端示例"""
    
    def __init__(self, base_url: str = "http://localhost:3001", 
                 protocol_version: str = "2.1"):
        """
        初始化 MCP 客户端
        
        Args:
            base_url: 服务器基础 URL
            protocol_version: MCP 协议版本
        """
        self.base_url = base_url.rstrip('/')
        self.protocol_version = protocol_version
        self.connection_id: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers={
                "MCP-Protocol-Version": self.protocol_version,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.connection_id:
            await self.disconnect()
        if self.session:
            await self.session.close()
            
    async def connect(self, client_info: Optional[Dict] = None) -> bool:
        """
        连接到 MCP 服务器
        
        Args:
            client_info: 客户端信息
            
        Returns:
            是否连接成功
        """
        try:
            if not client_info:
                client_info = {
                    "name": "Python MCP Client",
                    "version": "1.0.0"
                }
                
            async with self.session.post(
                f"{self.base_url}/connect",
                json={"client_info": client_info}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.connection_id = data["connection_id"]
                    logger.info(f"连接成功，连接ID: {self.connection_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"连接失败: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"连接异常: {e}")
            return False
            
    async def disconnect(self) -> bool:
        """断开连接"""
        if not self.connection_id:
            return True
            
        try:
            async with self.session.delete(
                f"{self.base_url}/disconnect/{self.connection_id}"
            ) as response:
                if response.status == 200:
                    logger.info("连接已断开")
                    self.connection_id = None
                    return True
                else:
                    logger.error(f"断开连接失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"断开连接异常: {e}")
            return False
            
    async def heartbeat(self) -> bool:
        """发送心跳"""
        if not self.connection_id:
            logger.warning("未连接，无法发送心跳")
            return False
            
        try:
            async with self.session.post(
                f"{self.base_url}/heartbeat/{self.connection_id}"
            ) as response:
                if response.status == 200:
                    logger.debug("心跳发送成功")
                    return True
                else:
                    logger.error(f"心跳发送失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"心跳发送异常: {e}")
            return False
            
    async def check_health(self) -> Dict[str, Any]:
        """检查服务器健康状态"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "code": response.status}
                    
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    async def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        try:
            async with self.session.get(f"{self.base_url}/info") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"error": str(e)}
            
    async def list_prompts(self) -> Dict[str, Any]:
        """列出所有可用提示"""
        try:
            headers = {}
            if self.connection_id:
                headers["X-Connection-ID"] = self.connection_id
                
            async with self.session.get(
                f"{self.base_url}/prompts",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"error": str(e)}
            
    async def execute_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行提示"""
        try:
            headers = {}
            if self.connection_id:
                headers["X-Connection-ID"] = self.connection_id
                
            async with self.session.post(
                f"{self.base_url}/prompts/{prompt_name}",
                json={"arguments": arguments},
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {"error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"error": str(e)}
            
    async def list_tools(self) -> Dict[str, Any]:
        """列出所有可用工具"""
        try:
            headers = {}
            if self.connection_id:
                headers["X-Connection-ID"] = self.connection_id
                
            async with self.session.get(
                f"{self.base_url}/tools",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"error": str(e)}
            
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            headers = {}
            if self.connection_id:
                headers["X-Connection-ID"] = self.connection_id
                
            async with self.session.post(
                f"{self.base_url}/tools/{tool_name}",
                json={"arguments": arguments},
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {"error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"error": str(e)}


async def demonstrate_client_usage():
    """演示客户端使用方法"""
    logger.info("开始 MCP 客户端演示")
    
    # 使用异步上下文管理器
    async with MCPClient("http://localhost:3001", "2.1") as client:
        
        # 1. 检查服务器健康状态
        logger.info("检查服务器健康状态...")
        health = await client.check_health()
        logger.info(f"健康状态: {json.dumps(health, indent=2, ensure_ascii=False)}")
        
        # 2. 获取服务器信息
        logger.info("获取服务器信息...")
        info = await client.get_server_info()
        logger.info(f"服务器信息: {json.dumps(info, indent=2, ensure_ascii=False)}")
        
        # 3. 连接到服务器
        logger.info("连接到服务器...")
        connected = await client.connect({
            "name": "演示客户端",
            "version": "1.0.0",
            "description": "MCP 客户端配置演示"
        })
        
        if not connected:
            logger.error("连接失败，退出演示")
            return
            
        # 4. 发送心跳
        logger.info("发送心跳...")
        await client.heartbeat()
        
        # 5. 列出可用提示
        logger.info("列出可用提示...")
        prompts = await client.list_prompts()
        logger.info(f"可用提示: {json.dumps(prompts, indent=2, ensure_ascii=False)}")
        
        # 6. 执行提示示例
        logger.info("执行需求生成提示...")
        result = await client.execute_prompt("generate-requirements", {
            "requirements": "一个简单的待办事项应用，支持任务创建、完成标记和本地存储"
        })
        logger.info(f"提示执行结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 7. 列出可用工具
        logger.info("列出可用工具...")
        tools = await client.list_tools()
        logger.info(f"可用工具: {json.dumps(tools, indent=2, ensure_ascii=False)}")
        
        # 8. 执行工具示例
        logger.info("执行文件创建工具...")
        tool_result = await client.execute_tool("create_file", {
            "path": "demo.txt",
            "content": "这是一个演示文件"
        })
        logger.info(f"工具执行结果: {json.dumps(tool_result, indent=2, ensure_ascii=False)}")
        
        # 9. 持续心跳演示
        logger.info("演示持续心跳...")
        for i in range(3):
            await asyncio.sleep(2)
            await client.heartbeat()
            logger.info(f"心跳 {i+1}/3 完成")
            
    logger.info("MCP 客户端演示完成")


async def demonstrate_ssl_connection():
    """演示 SSL 连接"""
    logger.info("演示 HTTPS 连接")
    
    # 注意：这需要服务器启用 SSL
    async with MCPClient("https://localhost:3001", "2.1") as client:
        health = await client.check_health()
        logger.info(f"HTTPS 健康检查: {json.dumps(health, indent=2, ensure_ascii=False)}")


async def demonstrate_error_handling():
    """演示错误处理"""
    logger.info("演示错误处理")
    
    # 连接到不存在的服务器
    async with MCPClient("http://localhost:9999", "2.1") as client:
        health = await client.check_health()
        logger.info(f"错误处理示例: {json.dumps(health, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demonstrate_client_usage())
    
    # 可选：演示其他功能
    # asyncio.run(demonstrate_ssl_connection())
    # asyncio.run(demonstrate_error_handling())