"""
Integration Tests for MCP + Prolog Validation (haiwpa_mcp.py)

Tests the validate_all_planned_workouts MCP tool.

Run with: pytest tests/test_mcp_integration.py -v
Servers required: MCP server must be running
    Start with: python haiwpa_mcp.py (runs on port 9000)
"""

import pytest
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import Client
import config


@pytest.fixture(scope="module")
def mcp_client():
    """Create MCP client for testing"""
    return Client(f"{config.MCP_SERVER_URL}/mcp")


class TestMCPConnection:
    """Tests for basic MCP server connection"""

    @pytest.mark.asyncio
    async def test_mcp_server_reachable(self, mcp_client):
        """Should be able to connect to MCP server"""
        try:
            async with mcp_client:
                tools = await mcp_client.list_tools()
                assert tools is not None
        except Exception as e:
            pytest.fail(f"Could not connect to MCP server: {e}\n"
                       f"Make sure MCP server is running: python haiwpa_mcp.py")

    @pytest.mark.asyncio
    async def test_validate_tool_exists(self, mcp_client):
        """Should have validate_all_planned_workouts tool available"""
        async with mcp_client:
            tools = await mcp_client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "validate_all_planned_workouts" in tool_names

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
