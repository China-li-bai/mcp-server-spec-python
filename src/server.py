"""Core MCP server implementation for Spec-Driven Development."""

from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, UserMessage


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    
    # Initialize FastMCP server
    mcp = FastMCP(
        name="Spec-Driven Development MCP Server",
        version="0.1.0"
    )
    
    @mcp.prompt()
    def generate_requirements(requirements: str) -> List[UserMessage]:
        """Generate requirements.md using EARS format.
        
        Args:
            requirements: High-level requirements of the application. 
                         Example: 'A Vue.js todo application with task creation, 
                         completion tracking, and local storage persistence'
        
        Returns:
            List of messages for the LLM to generate structured requirements document.
        """
        return [
            UserMessage(
                content=TextContent(
                    type="text",
                    text=f"""Based on below requirements, generate requirements.md using EARS format in 'specs' folder:

{requirements}"""
                )
            )
        ]
    
    @mcp.prompt()
    def generate_design_from_requirements() -> List[UserMessage]:
        """Generate design.md from requirements.md.
        
        Returns:
            List of messages for the LLM to generate design document from requirements.
        """
        return [
            UserMessage(
                content=TextContent(
                    type="text",
                    text="Based on specs/requirements.md, generate specs/design.md"
                )
            )
        ]
    
    @mcp.prompt()
    def generate_code_from_design() -> List[UserMessage]:
        """Generate code from design.md.
        
        Returns:
            List of messages for the LLM to generate implementation code from design.
        """
        return [
            UserMessage(
                content=TextContent(
                    type="text",
                    text="Based on specs/design.md, generate code on the root folder"
                )
            )
        ]
    
    return mcp


def get_server() -> FastMCP:
    """Get the configured MCP server instance."""
    return create_server()