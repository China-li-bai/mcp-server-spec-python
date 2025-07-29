#!/usr/bin/env python3
"""
基本使用示例

演示如何使用 Spec-Driven Development MCP Server
"""

import asyncio
import logging
from mcp_server_spec.server import create_server
from mcp_server_spec.http_stream import create_http_stream_server

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_stdio_server():
    """演示 stdio 服务器"""
    logger.info("=== 演示 stdio 服务器 ===")
    
    # 创建服务器
    server = create_server()
    
    # 获取提示定义
    prompt_definitions = server.prompt_manager.get_prompt_definitions()
    logger.info(f"可用提示: {list(prompt_definitions.keys())}")
    
    # 测试生成需求提示
    requirements = "一个Vue.js待办事项应用，具有任务创建、完成跟踪和本地存储持久化功能"
    response = server.prompt_manager.handle_prompt_request("generate-requirements", {
        "requirements": requirements
    })
    
    logger.info("生成的需求提示:")
    for msg in response.messages:
        logger.info(f"角色: {msg.role}")
        logger.info(f"内容: {msg.content['text'][:200]}...")


async def demo_http_stream_server():
    """演示 HTTP 流服务器"""
    logger.info("=== 演示 HTTP 流服务器 ===")
    
    # 创建 MCP 服务器
    mcp_server = create_server()
    
    # 创建 HTTP 流服务器
    http_server = create_http_stream_server(mcp_server)
    
    logger.info("HTTP 流服务器已创建")
    logger.info("可以通过以下端点访问:")
    logger.info("- GET /health - 健康检查")
    logger.info("- GET /prompts - 列出所有提示")
    logger.info("- POST /prompts/{prompt_name} - 获取特定提示")
    logger.info("- POST /prompts/{prompt_name}/stream - 获取流式提示")
    logger.info("- GET /server/info - 获取服务器信息")


async def demo_prompt_manager():
    """演示提示管理器"""
    logger.info("=== 演示提示管理器 ===")
    
    from mcp_server_spec.prompts import PromptManager
    
    prompt_manager = PromptManager()
    
    # 列出所有提示
    definitions = prompt_manager.get_prompt_definitions()
    logger.info("可用提示:")
    for name, definition in definitions.items():
        logger.info(f"- {name}: {definition['title']}")
    
    # 测试每个提示
    test_cases = [
        ("generate-requirements", {"requirements": "一个简单的博客系统"}),
        ("generate-design-from-requirements", {}),
        ("generate-code-from-design", {})
    ]
    
    for prompt_name, arguments in test_cases:
        logger.info(f"\n测试提示: {prompt_name}")
        try:
            response = prompt_manager.handle_prompt_request(prompt_name, arguments)
            logger.info(f"生成了 {len(response.messages)} 条消息")
            if response.messages:
                content = response.messages[0].content.get("text", "")
                logger.info(f"第一条消息预览: {content[:100]}...")
        except Exception as e:
            logger.error(f"处理提示时出错: {e}")


async def main():
    """主函数"""
    logger.info("Spec-Driven Development MCP Server 使用示例")
    logger.info("=" * 50)
    
    try:
        # 演示各个组件
        await demo_prompt_manager()
        await demo_stdio_server()
        await demo_http_stream_server()
        
        logger.info("\n演示完成！")
        logger.info("要运行实际的服务器，请使用:")
        logger.info("python -m mcp_server_spec.main --transport stdio")
        logger.info("python -m mcp_server_spec.main --transport http-stream --host 0.0.0.0 --port 3001")
        
    except Exception as e:
        logger.error(f"演示过程中出错: {e}")


if __name__ == "__main__":
    asyncio.run(main())