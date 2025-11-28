"""
Source : https://gofastmcp.com/getting-started/quickstart
"""

from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.resource("data://config")
def get_config() -> dict:
    return {"theme": "dark", "version": "1.0"}

if __name__ == "__main__":
    mcp.run()