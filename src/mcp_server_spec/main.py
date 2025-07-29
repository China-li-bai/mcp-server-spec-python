#!/usr/bin/env python3
"""
Spec-Driven Development MCP Server - 主入口点

支持多种传输方式：stdio、SSE、HTTP 流处理
"""

import argparse
import asyncio
import logging
import sys
from typing import Optional

from .server import create_server
from .http_stream import create_http_stream_server
from .enhanced_http_stream import create_enhanced_http_stream_server

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_stdio():
    """使用 stdio 传输运行服务器"""
    logger.info("启动 MCP 服务器 (stdio 传输)")
    server = create_server()
    await server.run_stdio()


async def run_sse(host: str = "localhost", port: int = 3001):
    """使用 SSE 传输运行服务器"""
    logger.info(f"启动 MCP 服务器 (SSE 传输) 在 http://{host}:{port}")
    server = create_server()
    await server.run_sse(host=host, port=port)


async def run_http_stream(host: str = "localhost", port: int = 3001, 
                         ssl_keyfile: str = None, ssl_certfile: str = None,
                         enhanced: bool = True):
    """使用 HTTP 流处理运行服务器"""
    protocol = "https" if ssl_keyfile and ssl_certfile else "http"
    logger.info(f"启动 MCP 服务器 (HTTP 流处理) 在 {protocol}://{host}:{port}")
    
    mcp_server = create_server()
    
    if enhanced:
        # 使用增强的 HTTP 流服务器
        http_server = create_enhanced_http_stream_server(mcp_server)
        await http_server.run(host=host, port=port, 
                             ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
    else:
        # 使用基础的 HTTP 流服务器
        http_server = create_http_stream_server(mcp_server)
        await http_server.run(host=host, port=port)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Spec-Driven Development MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
传输方式:
  stdio       - 标准输入输出传输 (默认)
  sse         - Server-Sent Events 传输
  http-stream - HTTP 流处理传输

示例:
  %(prog)s                           # 使用 stdio 传输
  %(prog)s --transport sse           # 使用 SSE 传输
  %(prog)s --transport http-stream   # 使用 HTTP 流处理
  %(prog)s --transport sse --host 0.0.0.0 --port 8080  # 自定义主机和端口
        """
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http-stream"],
        default="stdio",
        help="传输方式 (默认: stdio)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="服务器主机地址 (默认: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="服务器端口 (默认: 3001)"
    )
    
    parser.add_argument(
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )
    
    parser.add_argument(
        "--ssl-keyfile",
        help="SSL 私钥文件路径 (用于 HTTPS)"
    )
    
    parser.add_argument(
        "--ssl-certfile", 
        help="SSL 证书文件路径 (用于 HTTPS)"
    )
    
    parser.add_argument(
        "--enhanced",
        action="store_true",
        default=True,
        help="使用增强的 HTTP 流服务器 (默认: True)"
    )
    
    parser.add_argument(
        "--basic",
        action="store_true",
        help="使用基础的 HTTP 流服务器"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser.parse_args()


async def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
    try:
        if args.transport == "stdio":
            await run_stdio()
        elif args.transport == "sse":
            await run_sse(host=args.host, port=args.port)
        elif args.transport == "http-stream":
            # 检查 SSL 配置
            if args.ssl_keyfile and not args.ssl_certfile:
                logger.error("使用 SSL 时必须同时提供私钥文件和证书文件")
                sys.exit(1)
            if args.ssl_certfile and not args.ssl_keyfile:
                logger.error("使用 SSL 时必须同时提供私钥文件和证书文件")
                sys.exit(1)
                
            # 确定是否使用增强模式
            enhanced = not args.basic
            
            await run_http_stream(
                host=args.host, 
                port=args.port,
                ssl_keyfile=args.ssl_keyfile,
                ssl_certfile=args.ssl_certfile,
                enhanced=enhanced
            )
        else:
            logger.error(f"不支持的传输方式: {args.transport}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行时出错: {str(e)}")
        sys.exit(1)


def cli_main():
    """CLI 入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已关闭")
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()