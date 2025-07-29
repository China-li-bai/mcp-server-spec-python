#!/usr/bin/env python3
"""Main entry point for the Spec-Driven Development MCP Server (stdio transport)."""

import asyncio
import sys
from .server import create_server


async def main() -> None:
    """Main function to run the MCP server with stdio transport."""
    try:
        # Create the MCP server
        server = create_server()
        
        # Run the server with stdio transport
        await server.run()
        
    except Exception as error:
        print(f"Fatal error in main(): {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())