"""
提示模板管理

管理所有提示模板和生成逻辑
"""

import os
from typing import Any, Dict
from datetime import datetime

from .models import PromptResponse


class PromptManager:
    """提示管理器"""
    
    def __init__(self):
        """初始化提示管理器"""
        self.prompts = self._initialize_prompts()
        
    def _initialize_prompts(self) -> Dict[str, Dict[str, Any]]:
        """初始化提示定义"""
        prompts = {
            "generate-requirements": {
                "title": "生成需求文档",
                "description": "使用 EARS 格式生成 requirements.md",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "requirements": {
                            "type": "string",
                            "description": "应用程序的高级需求。例如：'一个带有任务创建、完成跟踪和本地存储持久化的 Vue.js 待办事项应用程序'"
                        }
                    },
                    "required": ["requirements"]
                }
            },
            "generate-design-from-requirements": {
                "title": "从需求生成设计",
                "description": "从 requirements.md 生成 design.md",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "requirements_path": {
                            "type": "string",
                            "description": "需求文档路径",
                            "default": "specs/requirements.md"
                        }
                    }
                }
            },
            "generate-code-from-design": {
                "title": "从设计生成代码",
                "description": "从 design.md 生成代码",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "design_path": {
                            "type": "string",
                            "description": "设计文档路径",
                            "default": "specs/design.md"
                        }
                    }
                }
            }
        }
        return prompts
        
    def handle_prompt_request(self, name: str, arguments: Dict[str, Any]) -> PromptResponse:
        """处理提示请求"""
        if name not in self.prompts:
            raise ValueError(f"未知提示: {name}")
            
        if name == "generate-requirements":
            return self.generate_requirements_prompt(arguments.get("requirements", ""))
        elif name == "generate-design-from-requirements":
            return self.generate_design_from_requirements_prompt(
                arguments.get("requirements_path", "specs/requirements.md")
            )
        elif name == "generate-code-from-design":
            return self.generate_code_from_design_prompt(
                arguments.get("design_path", "specs/design.md")
            )
        else:
            raise ValueError(f"未实现的提示处理器: {name}")
            
    def generate_requirements_prompt(self, requirements: str) -> PromptResponse:
        """生成需求文档提示"""
        prompt_content = f"""请基于以下高级需求，使用 EARS (Easy Approach to Requirements Syntax) 格式生成详细的需求文档。

高级需求：
{requirements}

请生成一个完整的 requirements.md 文档，包含以下部分：

# 需求文档

## 1. 项目概述
- 项目名称
- 项目描述
- 目标用户
- 主要目标

## 2. 功能需求 (使用 EARS 格式)

使用以下 EARS 模板：
- **WHEN** <可选的前提条件或触发器> **THE SYSTEM SHALL** <系统响应>
- **WHERE** <可选的功能适用场景> **THE SYSTEM SHALL** <系统响应>
- **WHILE** <可选的状态条件> **THE SYSTEM SHALL** <系统响应>

示例：
- WHEN 用户点击"添加任务"按钮 THE SYSTEM SHALL 显示任务创建表单
- WHERE 用户在任务列表页面 THE SYSTEM SHALL 显示所有未完成的任务
- WHILE 用户正在编辑任务 THE SYSTEM SHALL 自动保存更改

## 3. 非功能需求
- 性能要求
- 可用性要求
- 兼容性要求
- 安全性要求

## 4. 约束条件
- 技术约束
- 业务约束
- 时间约束

## 5. 验收标准
- 功能验收标准
- 性能验收标准
- 用户体验验收标准

请确保需求文档详细、清晰且可测试。将生成的内容保存到 specs/requirements.md 文件中。

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return PromptResponse(
            content=prompt_content,
            metadata={
                "prompt_type": "requirements_generation",
                "input_requirements": requirements,
                "output_file": "specs/requirements.md"
            }
        )
        
    def generate_design_from_requirements_prompt(self, requirements_path: str) -> PromptResponse:
        """从需求生成设计文档提示"""
        
        # 尝试读取需求文档
        requirements_content = ""
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    requirements_content = f.read()
            except Exception as e:
                requirements_content = f"无法读取需求文档: {str(e)}"
        else:
            requirements_content = f"需求文档不存在: {requirements_path}"
            
        prompt_content = f"""请基于以下需求文档生成详细的设计文档。

需求文档内容：
```
{requirements_content}
```

请生成一个完整的 design.md 文档，包含以下部分：

# 设计文档

## 1. 系统架构
- 整体架构图
- 技术栈选择
- 架构决策说明

## 2. 模块设计
- 核心模块划分
- 模块职责说明
- 模块间交互关系

## 3. 数据设计
- 数据模型设计
- 数据库设计（如适用）
- 数据流设计

## 4. 接口设计
- API 接口设计
- 用户界面设计
- 外部接口设计

## 5. 详细设计
- 关键算法设计
- 核心功能实现方案
- 错误处理机制

## 6. 安全设计
- 认证授权机制
- 数据安全保护
- 安全风险评估

## 7. 性能设计
- 性能优化策略
- 缓存策略
- 扩展性考虑

## 8. 部署设计
- 部署架构
- 环境配置
- 监控和日志

请确保设计文档与需求文档保持一致，并提供足够的技术细节用于后续的代码实现。将生成的内容保存到 specs/design.md 文件中。

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return PromptResponse(
            content=prompt_content,
            metadata={
                "prompt_type": "design_generation",
                "input_file": requirements_path,
                "output_file": "specs/design.md"
            }
        )
        
    def generate_code_from_design_prompt(self, design_path: str) -> PromptResponse:
        """从设计生成代码提示"""
        
        # 尝试读取设计文档
        design_content = ""
        if os.path.exists(design_path):
            try:
                with open(design_path, 'r', encoding='utf-8') as f:
                    design_content = f.read()
            except Exception as e:
                design_content = f"无法读取设计文档: {str(e)}"
        else:
            design_content = f"设计文档不存在: {design_path}"
            
        prompt_content = f"""请基于以下设计文档生成完整的代码实现。

设计文档内容：
```
{design_content}
```

请根据设计文档生成以下内容：

## 1. 项目结构
- 创建合适的目录结构
- 生成必要的配置文件
- 设置依赖管理文件

## 2. 核心代码实现
- 实现所有核心模块
- 遵循设计文档中的架构
- 包含适当的错误处理

## 3. 数据层实现
- 实现数据模型
- 实现数据访问层
- 包含数据验证逻辑

## 4. 业务逻辑实现
- 实现核心业务逻辑
- 实现服务层代码
- 包含业务规则验证

## 5. 接口层实现
- 实现 API 接口
- 实现用户界面（如适用）
- 包含输入验证和响应处理

## 6. 配置和部署
- 生成配置文件
- 创建部署脚本
- 包含环境变量配置

## 7. 测试代码
- 生成单元测试
- 生成集成测试
- 包含测试数据和模拟

## 8. 文档和说明
- 生成 README.md
- 创建 API 文档
- 包含使用说明

请确保生成的代码：
- 遵循最佳实践和编码规范
- 包含适当的注释和文档
- 具有良好的可读性和可维护性
- 与设计文档保持一致

将生成的代码文件保存到项目根目录的相应位置。

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return PromptResponse(
            content=prompt_content,
            metadata={
                "prompt_type": "code_generation",
                "input_file": design_path,
                "output_directory": "."
            }
        )
        
    def get_prompt_info(self, name: str) -> Dict[str, Any]:
        """获取提示信息"""
        if name not in self.prompts:
            raise ValueError(f"未知提示: {name}")
        return self.prompts[name]
        
    def list_prompts(self) -> Dict[str, Dict[str, Any]]:
        """列出所有提示"""
        return self.prompts.copy()