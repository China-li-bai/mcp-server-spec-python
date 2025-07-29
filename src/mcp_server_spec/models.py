"""
数据模型定义

使用 Pydantic 定义所有输入输出数据模型
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ServerInfo(BaseModel):
    """服务器信息"""
    name: str = Field(..., description="服务器名称")
    version: str = Field(..., description="服务器版本")
    description: str = Field(..., description="服务器描述")


class PromptRequest(BaseModel):
    """提示请求模型"""
    name: str = Field(..., description="提示名称")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="提示参数")


class PromptResponse(BaseModel):
    """提示响应模型"""
    content: str = Field(..., description="提示内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class RequirementsInput(BaseModel):
    """需求输入模型"""
    requirements: str = Field(..., description="高级需求描述")
    project_type: Optional[str] = Field(None, description="项目类型")
    additional_context: Optional[str] = Field(None, description="额外上下文")


class DesignInput(BaseModel):
    """设计输入模型"""
    requirements_path: str = Field(default="specs/requirements.md", description="需求文档路径")


class CodeInput(BaseModel):
    """代码输入模型"""
    design_path: str = Field(default="specs/design.md", description="设计文档路径")


class FileOperation(BaseModel):
    """文件操作模型"""
    path: str = Field(..., description="文件路径")
    content: Optional[str] = Field(None, description="文件内容")
    operation: str = Field(..., description="操作类型: create, read, update, delete")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: str = Field(..., description="时间戳")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


class PromptListResponse(BaseModel):
    """提示列表响应"""
    prompts: List[Dict[str, Any]] = Field(..., description="提示列表")


class ToolListResponse(BaseModel):
    """工具列表响应"""
    tools: List[Dict[str, Any]] = Field(..., description="工具列表")


class StreamResponse(BaseModel):
    """流响应模型"""
    type: str = Field(..., description="响应类型")
    data: Any = Field(..., description="响应数据")
    timestamp: Optional[str] = Field(None, description="时间戳")


class ConfigModel(BaseModel):
    """配置模型"""
    host: str = Field(default="localhost", description="服务器主机")
    port: int = Field(default=3001, description="服务器端口")
    log_level: str = Field(default="INFO", description="日志级别")
    transport: str = Field(default="stdio", description="传输方式")
    cors_origins: List[str] = Field(default=["*"], description="CORS 允许的源")
    max_request_size: int = Field(default=1024*1024, description="最大请求大小")