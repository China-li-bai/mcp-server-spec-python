#!/usr/bin/env python3
"""HTTP server implementation for the Spec-Driven Development MCP Server."""

import os
import sys
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from .server import create_server


# Create FastAPI app
app = FastAPI(
    title="Spec-Driven Development MCP Server",
    description="MCP Server for structured spec-driven development workflows",
    version="0.1.0"
)

# Create MCP server instance
mcp_server = create_server()


@app.on_event("startup")
async def startup_event():
    """Initialize the MCP server on startup."""
    try:
        print("MCP Server initialized successfully")
    except Exception as e:
        print(f"Failed to initialize MCP server: {e}", file=sys.stderr)
        sys.exit(1)


@app.post("/mcp")
async def handle_mcp_request(request: Request) -> JSONResponse:
    """Handle MCP requests via HTTP POST."""
    try:
        # Get the request body
        body = await request.json()
        print(f"Received MCP request: {body}")
        
        # For now, return a basic response indicating the server is running
        # In a full implementation, you would process the MCP request here
        response = {
            "jsonrpc": "2.0",
            "result": {
                "message": "MCP Server is running",
                "server_info": {
                    "name": "Spec-Driven Development MCP Server",
                    "version": "0.1.0"
                }
            },
            "id": body.get("id")
        }
        
        return JSONResponse(content=response)
        
    except Exception as error:
        print(f"Error handling MCP request: {error}", file=sys.stderr)
        
        # Return JSON-RPC error response
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal server error",
            },
            "id": body.get("id") if 'body' in locals() else None,
        }
        
        return JSONResponse(
            content=error_response,
            status_code=500
        )


@app.get("/mcp")
async def handle_mcp_get() -> JSONResponse:
    """Handle GET requests to /mcp (not allowed)."""
    print("Received GET MCP request")
    
    error_response = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32000,
            "message": "Method not allowed."
        },
        "id": None
    }
    
    return JSONResponse(
        content=error_response,
        status_code=405
    )


@app.delete("/mcp")
async def handle_mcp_delete() -> JSONResponse:
    """Handle DELETE requests to /mcp (not allowed)."""
    print("Received DELETE MCP request")
    
    error_response = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32000,
            "message": "Method not allowed."
        },
        "id": None
    }
    
    return JSONResponse(
        content=error_response,
        status_code=405
    )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "Spec-Driven Development MCP Server"}


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with basic information."""
    return {
        "name": "Spec-Driven Development MCP Server",
        "version": "0.1.0",
        "description": "MCP Server for structured spec-driven development workflows",
        "endpoints": {
            "mcp": "/mcp (POST only)",
            "health": "/health",
            "docs": "/docs"
        }
    }


def main() -> None:
    """Main function to run the HTTP server."""
    port = int(os.getenv("PORT", 3088))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Spec-Driven Development MCP Server on {host}:{port}")
    
    try:
        uvicorn.run(
            "src.http_server:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as error:
        print(f"Failed to start server: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()