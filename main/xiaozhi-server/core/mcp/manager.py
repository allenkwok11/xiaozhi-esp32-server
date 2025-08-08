"""MCP服务管理器"""

import asyncio
import os, json
from typing import Dict, Any, List
from .MCPClient import MCPClient
from plugins_func.register import register_function, ToolType
from config.config_loader import get_project_dir

TAG = __name__


class MCPManager:
    """管理多个MCP服务的集中管理器"""

    def __init__(self, conn) -> None:
        """
        初始化MCP管理器
        """
        self.conn = conn
        self.config_path = get_project_dir() + "data/.mcp_server_settings.json"
        if os.path.exists(self.config_path) == False:
            self.config_path = ""
            self.conn.logger.bind(tag=TAG).warning(
                f"please check mcp service config file：data/.mcp_server_settings.json"
            )
        self.client: Dict[str, MCPClient] = {}
        self.tools = []

    def load_config(self) -> Dict[str, Any]:
        """加载MCP服务配置
        Returns:
            Dict[str, Any]: 服务配置字典
        """
        if len(self.config_path) == 0:
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config.get("mcpServers", {})
        except Exception as e:
            self.conn.logger.bind(tag=TAG).error(
                f"Error loading MCP config from {self.config_path}: {e}"
            )
            return {}

    async def initialize_servers(self) -> None:
        """初始化所有MCP服务"""
        config = self.load_config()
        for name, srv_config in config.items():
            if not srv_config.get("command") and not srv_config.get("url"):
                self.conn.logger.bind(tag=TAG).warning(
                    f"Skipping server {name}: neither command nor url specified"
                )
                continue

            try:
                client = MCPClient(srv_config)
                await client.initialize()
                self.client[name] = client
                self.conn.logger.bind(tag=TAG).info(f"Initialized MCP client: {name}")
                client_tools = client.get_available_tools()
                self.tools.extend(client_tools)
                for tool in client_tools:
                    func_name = "mcp_" + tool["function"]["name"]
                    register_function(func_name, tool, ToolType.MCP_CLIENT)(
                        self.execute_tool
                    )
                    self.conn.func_handler.function_registry.register_function(
                        func_name
                    )

            except Exception as e:
                self.conn.logger.bind(tag=TAG).error(
                    f"Failed to initialize MCP server {name}: {e}"
                )
        self.conn.func_handler.upload_functions_desc()

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有服务的工具function定义
        Returns:
            List[Dict[str, Any]]: 所有工具的function定义列表
        """
        return self.tools

    def is_mcp_tool(self, tool_name: str) -> bool:
        """检查是否是MCP工具
        Args:
            tool_name: 工具名称
        Returns:
            bool: 是否是MCP工具
        """
        for tool in self.tools:
            if (
                tool.get("function") != None
                and tool["function"].get("name") == tool_name
            ):
                return True
        return False

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """执行工具调用
        Args:
            tool_name: 工具名称
            arguments: 工具参数
        Returns:
            Any: 工具执行结果
        Raises:
            ValueError: 工具未找到时抛出
        """
        
        # ====== DEBUG LOGGING ======
        self.conn.logger.bind(tag=TAG).info(f"🔍 DEBUG: execute_tool called with tool_name='{tool_name}', arguments={arguments}")
        
        # ====== TTS HANDLER - CONTAINER-FRIENDLY VERSION ======
        if tool_name == "tts/speak" or tool_name == "tts_speak":
            self.conn.logger.bind(tag=TAG).info(f"🎯 TTS HANDLER TRIGGERED!")
            try:
                import urllib.parse
                
                # Get and decode the text (handle URL encoding)
                raw_text = arguments.get('text', '')
                text = urllib.parse.unquote_plus(raw_text)  # Decode URL encoding
                voice = arguments.get('voice', 'santa')
                
                self.conn.logger.bind(tag=TAG).info(f"🎅 Santa speaking: {text} (decoded from: {raw_text})")
                
                # Add Santa character to the text
                if not text.lower().startswith('ho ho ho'):
                    santa_text = f"Ho ho ho! {text}"
                else:
                    santa_text = text
                
                import subprocess
                import os
                import time
                
                # Create audio directory if it doesn't exist
                audio_dir = "/tmp/santa_audio"
                os.makedirs(audio_dir, exist_ok=True)
                
                # Generate unique filename
                timestamp = int(time.time())
                audio_file = f"{audio_dir}/santa_{timestamp}.wav"
                
                try:
                    # Method 1: Generate WAV file with espeak (works in containers)
                    subprocess.run([
                        'espeak', 
                        '-s', '120',        # Speed: 120 words per minute
                        '-v', 'en+m3',      # Male voice variant 3
                        '-a', '200',        # Amplitude (volume)
                        '-w', audio_file,   # Write to WAV file
                        santa_text
                    ], check=True, timeout=15, capture_output=True)
                    
                    self.conn.logger.bind(tag=TAG).info(f"🎅 Santa audio generated: {audio_file}")
                    
                    # Try to play the file (this might work if Docker has audio access)
                    try:
                        # Method A: Try aplay (ALSA player)
                        subprocess.run(['aplay', audio_file], 
                                    check=True, timeout=10, capture_output=True)
                        self.conn.logger.bind(tag=TAG).info("🎅 Santa spoke via aplay")
                    except:
                        try:
                            # Method B: Try paplay (PulseAudio player)
                            subprocess.run(['paplay', audio_file], 
                                        check=True, timeout=10, capture_output=True)
                            self.conn.logger.bind(tag=TAG).info("🎅 Santa spoke via paplay")
                        except:
                            try:
                                # Method C: Try play (SoX player)
                                subprocess.run(['play', audio_file], 
                                            check=True, timeout=10, capture_output=True)
                                self.conn.logger.bind(tag=TAG).info("🎅 Santa spoke via play")
                            except:
                                # Audio playback failed, but file was created
                                self.conn.logger.bind(tag=TAG).warning(
                                    f"🎅 Santa audio file created but playback failed: {audio_file}"
                                )
                    
                    # Clean up old audio files (keep only last 10)
                    try:
                        audio_files = sorted([f for f in os.listdir(audio_dir) if f.startswith('santa_')])
                        if len(audio_files) > 10:
                            for old_file in audio_files[:-10]:
                                os.remove(os.path.join(audio_dir, old_file))
                    except:
                        pass
                    
                except Exception as espeak_error:
                    self.conn.logger.bind(tag=TAG).error(f"❌ Espeak error: {espeak_error}")
                    # Fallback: Just log the message clearly
                    self.conn.logger.bind(tag=TAG).info(f"🎅 SANTA SAYS: {santa_text}")
                    print(f"\n🎅 SANTA SAYS: {santa_text}\n")
                    audio_file = None
                
                return {
                    "success": True,
                    "message": f"🎅 Santa spoke: {text}",
                    "santa_text": santa_text,
                    "original_text": text,
                    "voice": voice,
                    "audio_file": audio_file,
                    "timestamp": timestamp
                }
                
            except Exception as e:
                self.conn.logger.bind(tag=TAG).error(f"❌ TTS Error: {e}")
                # Even if TTS fails, return the message
                fallback_text = f"Ho ho ho! {arguments.get('text', '')}"
                self.conn.logger.bind(tag=TAG).info(f"🎅 SANTA SAYS: {fallback_text}")
                print(f"\n🎅 SANTA SAYS: {fallback_text}\n")
                
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"🎅 Santa tried to say: {arguments.get('text', '')}",
                    "fallback_message": fallback_text
                }
        # ====== END TTS HANDLER ======
        
        # Original code continues here...
        self.conn.logger.bind(tag=TAG).info(
            f"Executing tool {tool_name} with arguments: {arguments}"
        )
        
        max_retries = 3  # 最大重试次数
        retry_interval = 2  # 重试间隔(秒)
        
        # 找到对应的客户端
        client_name = None
        target_client = None
        for name, client in self.client.items():
            if client.has_tool(tool_name):
                client_name = name
                target_client = client
                break
        
        if not target_client:
            raise ValueError(f"Tool {tool_name} not found in any MCP server")
        
        # 带重试机制的工具调用
        for attempt in range(max_retries):
            try:
                return await target_client.call_tool(tool_name, arguments)
            except Exception as e:
                # 最后一次尝试失败时直接抛出异常
                if attempt == max_retries - 1:
                    raise
                
                self.conn.logger.bind(tag=TAG).warning(
                    f"执行工具 {tool_name} 失败 (尝试 {attempt+1}/{max_retries}): {e}"
                )
                
                # 尝试重新连接
                self.conn.logger.bind(tag=TAG).info(
                    f"重试前尝试重新连接 MCP 客户端 {client_name}"
                )
                try:
                    # 关闭旧的连接
                    await target_client.cleanup()
                    
                    # 重新初始化客户端
                    config = self.load_config()
                    if client_name in config:
                        client = MCPClient(config[client_name])
                        await client.initialize()
                        self.client[client_name] = client
                        target_client = client                        
                        self.conn.logger.bind(tag=TAG).info(
                            f"成功重新连接 MCP 客户端: {client_name}"
                        )
                    else:
                        self.conn.logger.bind(tag=TAG).error(
                            f"Cannot reconnect MCP client {client_name}: config not found"
                        )
                except Exception as reconnect_error:
                    self.conn.logger.bind(tag=TAG).error(
                        f"Failed to reconnect MCP client {client_name}: {reconnect_error}"
                    )
                
                # 等待一段时间再重试
                await asyncio.sleep(retry_interval)
    async def cleanup_all(self) -> None:
        """Close all MCPClients one by one to prevent exceptions from interrupting the overall process"""
        for name, client in list(self.client.items()):
            try:
                await asyncio.wait_for(client.cleanup(), timeout=20)
                self.conn.logger.bind(tag=TAG).info(f"MCP client closed: {name}")
            except (asyncio.TimeoutError, Exception) as e:
                self.conn.logger.bind(tag=TAG).error(
                    f"Error closing MCP client {name}: {e}"
                )
        self.client.clear()
