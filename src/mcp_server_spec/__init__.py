"""
Spec-Driven Development MCP Server

一个基于 Model Context Protocol (MCP) 的规范驱动开发服务器，
支持需求生成、设计文档生成和代码实现生成。
"""

__version__ = "0.1.0"
__author__ = "Jun Han"
__description__ = "Spec-Driven Development MCP Server"

from .server import create_server, SpecDrivenMCPServer
from .models import PromptRequest, PromptResponse, ServerInfo
from .prompts import PromptManager

__all__ = [
    "create_server",
    "SpecDrivenMCPServer", 
    "PromptManager",
    "PromptRequest",
    "PromptResponse", 
    "ServerInfo",
]