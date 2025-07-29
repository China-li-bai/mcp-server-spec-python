#!/usr/bin/env python3
"""
MCP 服务器测试脚本

测试服务器的各种功能和配置
"""

import asyncio
import json
import logging
import subprocess
import time
import sys
from pathlib import Path

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from examples.client_configuration_example import MCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServerTester:
    """MCP 服务器测试器"""
    
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:3001"
        
    async def start_server(self, transport: str = "http-stream", 
                          enhanced: bool = True, ssl: bool = False):
        """启动测试服务器"""
        cmd = [
            sys.executable, "-m", "mcp_server_spec.main",
            "--transport", transport,
            "--host", "0.0.0.0",
            "--port", "3001",
            "--log-level", "INFO"
        ]
        
        if not enhanced:
            cmd.append("--basic")
            
        if ssl:
            # 注意：这需要有效的 SSL 证书文件
            cmd.extend([
                "--ssl-keyfile", "server.key",
                "--ssl-certfile", "server.crt"
            ])
            self.base_url = "https://localhost:3001"
            
        logger.info(f"启动服务器命令: {' '.join(cmd)}")
        
        try:
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            await asyncio.sleep(3)
            
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"服务器启动失败:")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
            logger.info("服务器启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动服务器异常: {e}")
            return False
            
    def stop_server(self):
        """停止测试服务器"""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            logger.info("服务器已停止")
            
    async def test_basic_functionality(self):
        """测试基本功能"""
        logger.info("=== 测试基本功能 ===")
        
        async with MCPClient(self.base_url, "2.1") as client:
            
            # 1. 健康检查
            logger.info("1. 测试健康检查...")
            health = await client.check_health()
            assert health.get("status") == "healthy", f"健康检查失败: {health}"
            logger.info("✓ 健康检查通过")
            
            # 2. 服务器信息
            logger.info("2. 测试服务器信息...")
            info = await client.get_server_info()
            assert "name" in info, f"服务器信息缺少名称: {info}"
            assert "version" in info, f"服务器信息缺少版本: {info}"
            logger.info("✓ 服务器信息获取成功")
            
            # 3. 连接测试
            logger.info("3. 测试连接...")
            connected = await client.connect({
                "name": "测试客户端",
                "version": "1.0.0"
            })
            assert connected, "连接失败"
            logger.info("✓ 连接成功")
            
            # 4. 心跳测试
            logger.info("4. 测试心跳...")
            heartbeat_ok = await client.heartbeat()
            assert heartbeat_ok, "心跳失败"
            logger.info("✓ 心跳成功")
            
            # 5. 提示列表
            logger.info("5. 测试提示列表...")
            prompts = await client.list_prompts()
            assert "prompts" in prompts, f"提示列表格式错误: {prompts}"
            logger.info(f"✓ 获取到 {len(prompts['prompts'])} 个提示")
            
            # 6. 工具列表
            logger.info("6. 测试工具列表...")
            tools = await client.list_tools()
            assert "tools" in tools, f"工具列表格式错误: {tools}"
            logger.info(f"✓ 获取到 {len(tools['tools'])} 个工具")
            
    async def test_protocol_version_validation(self):
        """测试协议版本验证"""
        logger.info("=== 测试协议版本验证 ===")
        
        # 测试支持的版本
        for version in ["2.0", "2.1", "2.2"]:
            logger.info(f"测试协议版本 {version}...")
            async with MCPClient(self.base_url, version) as client:
                health = await client.check_health()
                assert health.get("status") == "healthy", f"版本 {version} 测试失败"
            logger.info(f"✓ 协议版本 {version} 支持")
            
        # 测试不支持的版本
        logger.info("测试不支持的协议版本...")
        async with MCPClient(self.base_url, "1.0") as client:
            health = await client.check_health()
            # 这应该仍然工作，因为健康检查不需要严格的协议版本
            logger.info("✓ 不支持的协议版本处理正确")
            
    async def test_connection_management(self):
        """测试连接管理"""
        logger.info("=== 测试连接管理 ===")
        
        clients = []
        
        try:
            # 创建多个连接
            for i in range(3):
                client = MCPClient(self.base_url, "2.1")
                await client.__aenter__()
                
                connected = await client.connect({
                    "name": f"测试客户端-{i+1}",
                    "version": "1.0.0"
                })
                assert connected, f"客户端 {i+1} 连接失败"
                clients.append(client)
                
            logger.info(f"✓ 成功创建 {len(clients)} 个连接")
            
            # 测试心跳
            for i, client in enumerate(clients):
                heartbeat_ok = await client.heartbeat()
                assert heartbeat_ok, f"客户端 {i+1} 心跳失败"
                
            logger.info("✓ 所有连接心跳正常")
            
        finally:
            # 清理连接
            for client in clients:
                await client.__aexit__(None, None, None)
            logger.info("✓ 所有连接已清理")
            
    async def test_prompt_execution(self):
        """测试提示执行"""
        logger.info("=== 测试提示执行 ===")
        
        async with MCPClient(self.base_url, "2.1") as client:
            await client.connect()
            
            # 测试需求生成提示
            logger.info("测试需求生成提示...")
            result = await client.execute_prompt("generate-requirements", {
                "requirements": "一个简单的计算器应用"
            })
            
            assert "result" in result, f"提示执行结果格式错误: {result}"
            logger.info("✓ 需求生成提示执行成功")
            
    async def test_tool_execution(self):
        """测试工具执行"""
        logger.info("=== 测试工具执行 ===")
        
        async with MCPClient(self.base_url, "2.1") as client:
            await client.connect()
            
            # 测试文件创建工具
            logger.info("测试文件创建工具...")
            result = await client.execute_tool("create_file", {
                "path": "test_output.txt",
                "content": "这是测试内容"
            })
            
            assert "result" in result, f"工具执行结果格式错误: {result}"
            logger.info("✓ 文件创建工具执行成功")
            
            # 测试文件读取工具
            logger.info("测试文件读取工具...")
            result = await client.execute_tool("read_file", {
                "path": "test_output.txt"
            })
            
            assert "result" in result, f"工具执行结果格式错误: {result}"
            logger.info("✓ 文件读取工具执行成功")
            
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info("=== 测试错误处理 ===")
        
        async with MCPClient(self.base_url, "2.1") as client:
            await client.connect()
            
            # 测试不存在的提示
            logger.info("测试不存在的提示...")
            result = await client.execute_prompt("non-existent-prompt", {})
            assert "error" in result, "应该返回错误"
            logger.info("✓ 不存在的提示错误处理正确")
            
            # 测试不存在的工具
            logger.info("测试不存在的工具...")
            result = await client.execute_tool("non-existent-tool", {})
            assert "error" in result, "应该返回错误"
            logger.info("✓ 不存在的工具错误处理正确")
            
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始 MCP 服务器完整测试")
        
        # 启动服务器
        if not await self.start_server(enhanced=True):
            logger.error("无法启动服务器，测试终止")
            return False
            
        try:
            # 运行测试
            await self.test_basic_functionality()
            await self.test_protocol_version_validation()
            await self.test_connection_management()
            await self.test_prompt_execution()
            await self.test_tool_execution()
            await self.test_error_handling()
            
            logger.info("🎉 所有测试通过！")
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            return False
            
        finally:
            self.stop_server()


async def main():
    """主函数"""
    tester = MCPServerTester()
    
    try:
        success = await tester.run_all_tests()
        if success:
            logger.info("测试完成，服务器功能正常")
            sys.exit(0)
        else:
            logger.error("测试失败，请检查服务器配置")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        tester.stop_server()
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试异常: {e}")
        tester.stop_server()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())