import json
import asyncio
from concurrent.futures import Future
from core.utils.util import get_vision_url, sanitize_tool_name
from core.utils.auth import AuthToken
from core.providers.tts.dto.dto import ContentType
from core.utils.dialogue import Message

TAG = __name__


class MCPClient:
    """MCPClient，用于管理MCP状态和工具"""

    def __init__(self):
        self.tools = {}  # sanitized_name -> tool_data
        self.name_mapping = {}
        self.ready = False
        self.call_results = {}  # To store Futures for tool call responses
        self.next_id = 1
        self.lock = asyncio.Lock()
        self._cached_available_tools = None  # Cache for get_available_tools

    def has_tool(self, name: str) -> bool:
        return name in self.tools

    def get_available_tools(self) -> list:
        # Check if the cache is valid
        if self._cached_available_tools is not None:
            return self._cached_available_tools

        # If cache is not valid, regenerate the list
        result = []
        for tool_name, tool_data in self.tools.items():
            function_def = {
                "name": tool_name,
                "description": tool_data["description"],
                "parameters": {
                    "type": tool_data["inputSchema"].get("type", "object"),
                    "properties": tool_data["inputSchema"].get("properties", {}),
                    "required": tool_data["inputSchema"].get("required", []),
                },
            }
            result.append({"type": "function", "function": function_def})

        self._cached_available_tools = result  # Store the generated list in cache
        return result

    async def is_ready(self) -> bool:
        async with self.lock:
            return self.ready

    async def set_ready(self, status: bool):
        async with self.lock:
            self.ready = status

    async def add_tool(self, tool_data: dict):
        async with self.lock:
            sanitized_name = sanitize_tool_name(tool_data["name"])
            self.tools[sanitized_name] = tool_data
            self.name_mapping[sanitized_name] = tool_data["name"]
            self._cached_available_tools = (
                None  # Invalidate the cache when a tool is added
            )

    async def get_next_id(self) -> int:
        async with self.lock:
            current_id = self.next_id
            self.next_id += 1
            return current_id

    async def register_call_result_future(self, id: int, future: Future):
        async with self.lock:
            self.call_results[id] = future

    async def resolve_call_result(self, id: int, result: any):
        async with self.lock:
            if id in self.call_results:
                future = self.call_results.pop(id)
                if not future.done():
                    future.set_result(result)

    async def reject_call_result(self, id: int, exception: Exception):
        async with self.lock:
            if id in self.call_results:
                future = self.call_results.pop(id)
                if not future.done():
                    future.set_exception(exception)

    async def cleanup_call_result(self, id: int):
        async with self.lock:
            if id in self.call_results:
                self.call_results.pop(id)


async def send_mcp_message(conn, payload: dict):
    """Helper to send MCP messages, encapsulating common logic."""
    if not conn.features.get("mcp"):
        conn.logger.bind(tag=TAG).warning("Server-side does not support MCP, cannot send MCP message")
        return

    message = json.dumps({"type": "mcp", "payload": payload})

    try:
        await conn.websocket.send(message)
        conn.logger.bind(tag=TAG).info(f"Successfully send MCP message: {message}")
    except Exception as e:
        conn.logger.bind(tag=TAG).error(f"failed to send MCP message: {e}")


async def handle_mcp_message(conn, mcp_client: MCPClient, payload: dict):
    """处理MCP消息,包括初始化、工具列表和工具调用响应等"""
    conn.logger.bind(tag=TAG).info(f"handling MCP message: {payload}")

    if not isinstance(payload, dict):
        conn.logger.bind(tag=TAG).error("MCP message lacks payload fields or format exception")
        return

    # Handle result
    if "result" in payload:
        result = payload["result"]
        msg_id = int(payload.get("id", 0))

        # Check for tool call response first
        if msg_id in mcp_client.call_results:
            conn.logger.bind(tag=TAG).debug(
                f"response of calling tool received, ID: {msg_id}, result: {result}"
            )
            await mcp_client.resolve_call_result(msg_id, result)
            return

        if msg_id == 1:  # mcpInitializeID
            conn.logger.bind(tag=TAG).debug("MCP initializtion response received")
            server_info = result.get("serverInfo")
            if isinstance(server_info, dict):
                name = server_info.get("name")
                version = server_info.get("version")
                conn.logger.bind(tag=TAG).info(
                    f"client-side MCP server message: name={name}, version={version}"
                )
            return

        elif msg_id == 2:  # mcpToolsListID
            conn.logger.bind(tag=TAG).debug("MCP tool list response received")
            if isinstance(result, dict) and "tools" in result:
                tools_data = result["tools"]
                if not isinstance(tools_data, list):
                    conn.logger.bind(tag=TAG).error("tool list format error")
                    return

                conn.logger.bind(tag=TAG).info(
                    f"tool amounts supported by client-side device: {len(tools_data)}"
                )

                for i, tool in enumerate(tools_data):
                    if not isinstance(tool, dict):
                        continue

                    name = tool.get("name", "")
                    description = tool.get("description", "")
                    input_schema = {"type": "object", "properties": {}, "required": []}

                    if "inputSchema" in tool and isinstance(tool["inputSchema"], dict):
                        schema = tool["inputSchema"]
                        input_schema["type"] = schema.get("type", "object")
                        input_schema["properties"] = schema.get("properties", {})
                        input_schema["required"] = [
                            s for s in schema.get("required", []) if isinstance(s, str)
                        ]

                    new_tool = {
                        "name": name,
                        "description": description,
                        "inputSchema": input_schema,
                    }
                    await mcp_client.add_tool(new_tool)
                    conn.logger.bind(tag=TAG).debug(f"client-side tool #{i+1}: {name}")

                # 替换所有工具描述中的工具名称
                for tool_data in mcp_client.tools.values():
                    if "description" in tool_data:
                        description = tool_data["description"]
                        # 遍历所有工具名称进行替换
                        for (
                            sanitized_name,
                            original_name,
                        ) in mcp_client.name_mapping.items():
                            description = description.replace(
                                original_name, sanitized_name
                            )
                        tool_data["description"] = description

                next_cursor = result.get("nextCursor", "")
                if next_cursor:
                    conn.logger.bind(tag=TAG).info(
                        f"more tool, nextCursor: {next_cursor}"
                    )
                    await send_mcp_tools_list_continue_request(conn, next_cursor)
                else:
                    await mcp_client.set_ready(True)
                    conn.logger.bind(tag=TAG).info("all tool acquired, MCP client-side ready")
            return

    # Handle method calls (requests from the client)
    elif "method" in payload:
        method = payload["method"]
        conn.logger.bind(tag=TAG).info(f"MCP client-side request received: {method}")

        # ====== SANTA TTS HANDLER (PLUGIN-BASED VERSION) ======
        if method == "tts/speak":
            try:
                import urllib.parse
                
                # Get parameters
                params = payload.get("params", {})
                raw_text = params.get('text', '')
                text = urllib.parse.unquote_plus(raw_text)  # Decode URL encoding
                
                conn.logger.bind(tag=TAG).info(f"🎅 Received Santa speak request: {text}")
                
                # Use the santa_speak plugin function
                from plugins_func.functions.santa_speak import santa_speak
                
                # Call the plugin function
                response = santa_speak(conn, text)
                
                # Send success response back to client
                response_payload = {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "result": {
                        "success": True, 
                        "message": response.response, 
                        "text": text
                    }
                }
                await send_mcp_message(conn, response_payload)
                return
                
            except Exception as e:
                conn.logger.bind(tag=TAG).error(f"❌ Santa TTS Error: {e}")
                import traceback
                conn.logger.bind(tag=TAG).error(f"❌ Full error: {traceback.format_exc()}")
                
                # Send error response back to client
                error_payload = {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "error": {"code": -1, "message": f"Santa TTS failed: {str(e)}"}
                }
                await send_mcp_message(conn, error_payload)
                return
        # ====== SYSTEM QUIT HANDLER ======
        if method in ("self_system_quit", "self.system.quit", "system.quit", "system/quit"):
            try:
                params = payload.get("params", {}) or {}
                goodbye_text = params.get("say_goodbye") or params.get("text") or "Goodbye"
                conn.logger.bind(tag=TAG).info(f"Received quit request from client, saying goodbye: {goodbye_text}")
                try:
                    if goodbye_text and hasattr(conn, "tts") and conn.tts:
                        conn.tts.tts_one_sentence(conn, ContentType.TEXT, content_detail=goodbye_text)
                        conn.dialogue.put(Message(role="assistant", content=goodbye_text))
                except Exception as e:
                    conn.logger.bind(tag=TAG).error(f"failed to play goodbye TTS: {e}")

                # close connection
                await conn.close(conn.websocket)
                return
            except Exception as e:
                conn.logger.bind(tag=TAG).error(f"error handling quit request: {e}")
        # ====== END SANTA TTS HANDLER ======

    elif "error" in payload:
        error_data = payload["error"]
        error_msg = error_data.get("message", "unknown error")
        conn.logger.bind(tag=TAG).error(f"MCP error response received: {error_msg}")

        msg_id = int(payload.get("id", 0))
        if msg_id in mcp_client.call_results:
            await mcp_client.reject_call_result(
                msg_id, Exception(f"MCP error: {error_msg}")
            )


# --- Outgoing MCP Messages ---


async def send_mcp_initialize_message(conn):
    """发送MCP初始化消息"""

    vision_url = get_vision_url(conn.config)

    # 密钥生成token
    auth = AuthToken(conn.config["server"]["auth_key"])
    token = auth.generate_token(conn.headers.get("device-id"))

    vision = {
        "url": vision_url,
        "token": token,
    }

    payload = {
        "jsonrpc": "2.0",
        "id": 1,  # mcpInitializeID
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {},
                "vision": vision,
            },
            "clientInfo": {
                "name": "XiaozhiClient",
                "version": "1.0.0",
            },
        },
    }
    conn.logger.bind(tag=TAG).info("send MCP initialization message")
    await send_mcp_message(conn, payload)


async def send_mcp_tools_list_request(conn):
    """发送MCP工具列表请求"""
    payload = {
        "jsonrpc": "2.0",
        "id": 2,  # mcpToolsListID
        "method": "tools/list",
    }
    conn.logger.bind(tag=TAG).debug("send MCP tool list request")
    await send_mcp_message(conn, payload)


async def send_mcp_tools_list_continue_request(conn, cursor: str):
    """发送带有cursor的MCP工具列表请求"""
    payload = {
        "jsonrpc": "2.0",
        "id": 2,  # mcpToolsListID (same ID for continuation)
        "method": "tools/list",
        "params": {"cursor": cursor},
    }
    conn.logger.bind(tag=TAG).info(f"send MCP tool list with cursor request: {cursor}")
    await send_mcp_message(conn, payload)


async def call_mcp_tool(
    conn, mcp_client: MCPClient, tool_name: str, args: str = "{}", timeout: int = 30
):
    """
    调用指定的工具，并等待响应
    """
    if not await mcp_client.is_ready():
        raise RuntimeError("MCP client-side not ready")

    if not mcp_client.has_tool(tool_name):
        raise ValueError(f"tool {tool_name} does not exist")

    tool_call_id = await mcp_client.get_next_id()
    result_future = asyncio.Future()
    await mcp_client.register_call_result_future(tool_call_id, result_future)

    # 处理参数
    try:
        if isinstance(args, str):
            # 确保字符串是有效的JSON
            if not args.strip():
                arguments = {}
            else:
                try:
                    # 尝试直接解析
                    arguments = json.loads(args)
                except json.JSONDecodeError:
                    # 如果解析失败，尝试合并多个JSON对象
                    try:
                        # 使用正则表达式匹配所有JSON对象
                        import re

                        json_objects = re.findall(r"\{[^{}]*\}", args)
                        if len(json_objects) > 1:
                            # 合并所有JSON对象
                            merged_dict = {}
                            for json_str in json_objects:
                                try:
                                    obj = json.loads(json_str)
                                    if isinstance(obj, dict):
                                        merged_dict.update(obj)
                                except json.JSONDecodeError:
                                    continue
                            if merged_dict:
                                arguments = merged_dict
                            else:
                                raise ValueError(f"cannot analyze any valid JSON object: {args}")
                        else:
                            raise ValueError(f"failed to analyze parameter JSON: {args}")
                    except Exception as e:
                        conn.logger.bind(tag=TAG).error(
                            f"parameter JSON analysis failed: {str(e)}, original parameter: {args}"
                        )
                        raise ValueError(f"parameter JSON analysis failed: {str(e)}")
        elif isinstance(args, dict):
            arguments = args
        else:
            raise ValueError(f"parameter type error, string and dictionary expected, actual type is: {type(args)}")

        # 确保参数是字典类型
        if not isinstance(arguments, dict):
            raise ValueError(f"parameter must be dictionary type, actualy type is: {type(arguments)}")

    except Exception as e:
        if not isinstance(e, ValueError):
            raise ValueError(f"parameter handling failed: {str(e)}")
        raise e

    actual_name = mcp_client.name_mapping.get(tool_name, tool_name)
    payload = {
        "jsonrpc": "2.0",
        "id": tool_call_id,
        "method": "tools/call",
        "params": {"name": actual_name, "arguments": arguments},
    }

    conn.logger.bind(tag=TAG).info(
        f"send client-side mcp-tool calling request: {actual_name}, parameter: {args}"
    )
    await send_mcp_message(conn, payload)

    try:
        # Wait for response or timeout
        raw_result = await asyncio.wait_for(result_future, timeout=timeout)
        conn.logger.bind(tag=TAG).info(
            f"client-side MCp tool calling {actual_name}  successed, original result: {raw_result}"
        )

        if isinstance(raw_result, dict):
            if raw_result.get("isError") is True:
                error_msg = raw_result.get(
                    "error", "Tool calling returned error, but no specific error info was provided"
                )
                raise RuntimeError(f"tool calling error: {error_msg}")

            content = raw_result.get("content")
            if isinstance(content, list) and len(content) > 0:
                if isinstance(content[0], dict) and "text" in content[0]:
                    # 直接返回文本内容，不进行JSON解析
                    return content[0]["text"]
        # 如果结果不是预期的格式，将其转换为字符串
        return str(raw_result)
    except asyncio.TimeoutError:
        await mcp_client.cleanup_call_result(tool_call_id)
        raise TimeoutError("tool calling request timeout")
    except Exception as e:
        await mcp_client.cleanup_call_result(tool_call_id)
        raise e
