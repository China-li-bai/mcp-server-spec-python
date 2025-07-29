#!/usr/bin/env python3
"""Simple syntax test for the MCP server implementation."""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from server import create_server
    print("✓ Server module imported successfully")
    
    # Test server creation
    server = create_server()
    print("✓ Server created successfully")
    print(f"✓ Server name: {server.name}")
    print(f"✓ Server version: {server.version}")
    
    print("\n🎉 All syntax tests passed!")
    print("\nThe MCP server implementation is ready to use.")
    print("\nTo run the server:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run stdio version: python src/main.py")
    print("3. Run HTTP version: python src/http_server.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)