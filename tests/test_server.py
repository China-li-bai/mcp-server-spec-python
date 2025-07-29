"""
测试 MCP 服务器功能
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from mcp_server_spec.server import create_server, SpecDrivenMCPServer
from mcp_server_spec.prompts import PromptManager
from mcp_server_spec.models import RequirementsInput


class TestSpecDrivenMCPServer:
    """测试规范驱动 MCP 服务器"""
    
    def test_create_server(self):
        """测试创建服务器"""
        server = create_server()
        assert isinstance(server, SpecDrivenMCPServer)
        assert server.server_info.name == "Spec-Driven Development MCP Server"
        assert server.server_info.version == "0.1.0"
    
    def test_server_initialization(self):
        """测试服务器初始化"""
        server = SpecDrivenMCPServer()
        assert server.prompt_manager is not None
        assert isinstance(server.prompt_manager, PromptManager)


class TestPromptManager:
    """测试提示管理器"""
    
    def setup_method(self):
        """设置测试方法"""
        self.prompt_manager = PromptManager()
    
    def test_get_prompt_definitions(self):
        """测试获取提示定义"""
        definitions = self.prompt_manager.get_prompt_definitions()
        assert isinstance(definitions, dict)
        assert "generate-requirements" in definitions
        assert "generate-design-from-requirements" in definitions
        assert "generate-code-from-design" in definitions
    
    def test_get_prompt_definition(self):
        """测试获取特定提示定义"""
        definition = self.prompt_manager.get_prompt_definition("generate-requirements")
        assert definition is not None
        assert definition["title"] == "生成需求文档"
        assert "requirements" in definition["args_schema"]["properties"]
    
    def test_generate_requirements_prompt(self):
        """测试生成需求文档提示"""
        requirements = "一个简单的待办事项应用"
        response = self.prompt_manager.generate_requirements_prompt(requirements)
        
        assert len(response.messages) == 1
        assert response.messages[0].role == "user"
        assert requirements in response.messages[0].content["text"]
        assert "EARS" in response.messages[0].content["text"]
    
    def test_generate_design_from_requirements_prompt(self):
        """测试从需求生成设计文档提示"""
        response = self.prompt_manager.generate_design_from_requirements_prompt()
        
        assert len(response.messages) == 1
        assert response.messages[0].role == "user"
        assert "specs/requirements.md" in response.messages[0].content["text"]
        assert "specs/design.md" in response.messages[0].content["text"]
    
    def test_generate_code_from_design_prompt(self):
        """测试从设计生成代码提示"""
        response = self.prompt_manager.generate_code_from_design_prompt()
        
        assert len(response.messages) == 1
        assert response.messages[0].role == "user"
        assert "specs/design.md" in response.messages[0].content["text"]
    
    def test_handle_prompt_request_requirements(self):
        """测试处理需求提示请求"""
        arguments = {"requirements": "测试需求"}
        response = self.prompt_manager.handle_prompt_request("generate-requirements", arguments)
        
        assert len(response.messages) == 1
        assert "测试需求" in response.messages[0].content["text"]
    
    def test_handle_prompt_request_design(self):
        """测试处理设计提示请求"""
        response = self.prompt_manager.handle_prompt_request("generate-design-from-requirements", {})
        
        assert len(response.messages) == 1
        assert "specs/requirements.md" in response.messages[0].content["text"]
    
    def test_handle_prompt_request_code(self):
        """测试处理代码提示请求"""
        response = self.prompt_manager.handle_prompt_request("generate-code-from-design", {})
        
        assert len(response.messages) == 1
        assert "specs/design.md" in response.messages[0].content["text"]
    
    def test_handle_prompt_request_invalid(self):
        """测试处理无效提示请求"""
        with pytest.raises(ValueError, match="未知的提示名称"):
            self.prompt_manager.handle_prompt_request("invalid-prompt", {})
    
    def test_handle_prompt_request_missing_requirements(self):
        """测试处理缺少需求参数的请求"""
        with pytest.raises(ValueError, match="需求参数是必需的"):
            self.prompt_manager.handle_prompt_request("generate-requirements", {})


class TestModels:
    """测试数据模型"""
    
    def test_requirements_input_valid(self):
        """测试有效的需求输入"""
        requirements = RequirementsInput(requirements="这是一个测试需求")
        assert requirements.requirements == "这是一个测试需求"
    
    def test_requirements_input_too_short(self):
        """测试过短的需求输入"""
        with pytest.raises(ValueError):
            RequirementsInput(requirements="短")
    
    def test_requirements_input_too_long(self):
        """测试过长的需求输入"""
        long_requirements = "x" * 5001
        with pytest.raises(ValueError):
            RequirementsInput(requirements=long_requirements)


if __name__ == "__main__":
    pytest.main([__file__])