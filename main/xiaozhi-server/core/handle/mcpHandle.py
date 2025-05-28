

import json

TAG = __name__

async def handleMCPMessage(conn, payload):
    """处理MCP消息"""
    if not conn.features.get("mcp"):
        conn.logger.bind(tag=TAG).warning("客户端不支持MCP，忽略消息")
        return

    if payload.get("jsonrpc") != "2.0":
        conn.logger.bind(tag=TAG).error("MCP消息格式错误，缺少jsonrpc字段")
        return
    
    if "id" not in payload or not isinstance(payload["id"], int):
        # MCP消息必须包含id字段，且id必须是整数
        conn.logger.bind(tag=TAG).error("MCP消息格式错误，缺少id字段")
        return

    # payload必须包含result,而result中包含tools、content、isError（默认False）
    if "result" not in payload:
        conn.logger.bind(tag=TAG).error("MCP消息格式错误，缺少result字段")
        return
    # tools是一个列表，包含所有可用的工具,tools中每个工具必须包含name和description字段和inputSchema字段，如果有tools则处理
    if "tools" in payload["result"]:
        tools = payload["result"]["tools"]
        if not isinstance(tools, list):
            conn.logger.bind(tag=TAG).error("MCP消息格式错误，tools字段不是列表")
            return
        for tool in tools:
            if not isinstance(tool, dict) or "name" not in tool or "description" not in tool:
                conn.logger.bind(tag=TAG).error("MCP消息格式错误，tools中的工具缺少name或description字段")
                return
            # 处理工具注册逻辑
            
        conn.logger.bind(tag=TAG).info(f"注册了{len(tools)}个MCP工具")
    # content是一个数组，每个元素包含type和text,包含消息内容，是回复mcp的内容，如果有则进行处理
    if "content" in payload["result"]:
        content = payload["result"]["content"]
        if not isinstance(content, list):
            conn.logger.bind(tag=TAG).error("MCP消息格式错误，content字段不是列表")
            return
        for item in content:
            if not isinstance(item, dict) or "type" not in item or "text" not in item:
                conn.logger.bind(tag=TAG).error("MCP消息格式错误，content中的元素缺少type或text字段")
                return
            if item["type"] == "text":
                # 处理文本消息
                pass  # TODO: Implement text message handling

async def send_mcp_response(conn, payload):
    """发送MCP响应"""
    if not conn.features.get("mcp"):
        conn.logger.bind(tag=__name__).warning("客户端不支持MCP，无法发送MCP消息")
        return

    # payload中id必须是整数，必须递增，如果传递了id，z则使用id,否则需要生成一个id
    id = payload.get("id")
    if id is not None and not isinstance(id, int):
        conn.logger.bind(tag=__name__).error("MCP消息ID必须是整数")
        return
    if id is None:
        # 生成一个新的ID，通常是递增的， mcp_next_id可能为空,需要考虑并发
        if not hasattr(conn, 'mcp_next_id'):
            conn.mcp_next_id = 1
        id = conn.mcp_next_id
        conn.mcp_next_id += 1
    elif not isinstance(id, int):
        conn.logger.bind(tag=__name__).error("MCP消息ID必须是整数")
        return

    payload["id"] = id
    # MCP消息格式为JSON字符串
    message = json.dumps({
        "type": "mcp",
        "payload": payload
    })

    try:
        await conn.websocket.send(message)
        conn.logger.bind(tag=__name__).info(f"成功发送MCP消息: {message}")
    except Exception as e:
        conn.logger.bind(tag=__name__).error(f"发送MCP消息失败: {e}")

async def send_mcp_initialized(conn):
    """发送MCP初始化通知"""
    if not conn.features.get("mcp"):
        conn.logger.bind(tag=__name__).warning("客户端不支持MCP，无法发送初始化通知")
        return

    payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }

    await send_mcp_response(conn, payload)

async def send_mcp_tools_list(conn):
    """发送MCP工具列表"""
    if not conn.features.get("mcp"):
        conn.logger.bind(tag=__name__).warning("客户端不支持MCP，无法发送工具列表")
        return

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {}
    }

    await send_mcp_response(conn, payload)

async def send_mcp_tool_call(conn, tool_name, params):
    """发送MCP工具调用请求"""
    if not conn.features.get("mcp"):
        conn.logger.bind(tag=__name__).warning("客户端不支持MCP，无法发送工具调用请求")
        return

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        }
    }

    await send_mcp_response(conn, payload)