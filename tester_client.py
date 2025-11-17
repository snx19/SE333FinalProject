#!/usr/bin/env python3
"""Client to interact with the tester agent via MCP"""

import httpx
import json
import sys

# MCP server endpoint (adjust if running on different host/port)
MCP_SERVER_URL = "http://localhost:8000"

async def call_mcp_tool(tool_name: str, **kwargs) -> str:
    """Call an MCP tool via HTTP"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{MCP_SERVER_URL}/tool/{tool_name}",
                json=kwargs,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error calling {tool_name}: {e}"

def main():
    """Main tester client"""
    print("🧪 Tester Agent Client")
    print("=" * 50)
    
    # Example: Use the add tool for math calculations
    print("\n1️⃣  Testing math calculation (add):")
    print("   Calculating 1 + 2...")
    # Note: In a real async context, you'd use asyncio.run()
    # For now, this demonstrates the intended interface
    
    print("\n📝 Available tools:")
    print("   - add(a: int, b: int) -> int")
    print("   - generate_tests(java_file_path: str) -> str")
    print("   - run_tests() -> str")
    
    print("\n💡 To use the tester agent:")
    print("   1. Start the server: python server.py")
    print("   2. Connect with this client")
    print("   3. Call tools via MCP interface")

if __name__ == "__main__":
    main()
