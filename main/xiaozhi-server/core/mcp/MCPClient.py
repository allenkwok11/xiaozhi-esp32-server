import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config.logger import setup_logging

TAG = __name__

class MCPClient:
    def __init__(self, config):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.logger = setup_logging()
        self.config = config
        self.tolls = []

    async def initialize(self):
        main_command = self.config["command"]
        args = self.config.get("args", [])

        server_script_path = main_command
        if args:
            # 如果第一个参数是路径，使用其目录作为工作目录
            possible_path = args[0]
            if os.path.exists(possible_path):
                server_script_path = possible_path
        await self.connect_to_server(server_script_path)


    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        
        env = self.config.get("env", {})
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=env
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        self.tools = tools
        self.logger.bind(tag=TAG).info(f"Connected to server with tools:{[tool.name for tool in tools]}")

    def get_available_tools(self):
        available_tools = [{"type": "function", "function":{ 
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        } } for tool in self.tools]

        return available_tools
    
    async def call_tool(self, tool_name: str, tool_args: dict):
        response = await self.session.call_tool(tool_name, tool_args)
        return response

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())