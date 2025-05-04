from __future__ import annotations

import asyncio, os, shutil, concurrent.futures
from datetime import timedelta
from contextlib import AsyncExitStack
from typing import Optional, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config.logger import setup_logging

TAG = __name__


class MCPClient:
    def __init__(self, config: dict):
        self.logger = setup_logging()
        self.config = config

        # Back‑worker task & 状态同步
        self._worker_task: Optional[asyncio.Task] = None
        self._ready_evt = asyncio.Event()
        self._shutdown_evt = asyncio.Event()

        # 运行时资源
        self.session: Optional[ClientSession] = None
        self.tools: List = []

    async def initialize(self):
        """
        启动后台 task，并等待其就绪（拿到 `tools`）。
        """
        if self._worker_task:
            return  # 已经 init 过

        # 在当前 loop 创建后台 task
        self._worker_task = asyncio.create_task(self._worker(), name="MCPClientWorker")
        await self._ready_evt.wait()  # 等待 worker 初始化完成

        # 此时 tools 已填充
        self.logger.bind(tag=TAG).info(
            f"Connected, tools = {[t.name for t in self.tools]}"
        )

    async def cleanup(self):
        """
        对外关闭接口：
            · 只负责发出 “关机信号”
            · 等待后台 task 正常退出
        在任何 loop / task 调用都安全。
        """
        if not self._worker_task:
            return

        self._shutdown_evt.set()  # 发信号
        try:
            await asyncio.wait_for(self._worker_task, timeout=15)
        except (asyncio.TimeoutError, Exception) as e:
            self.logger.bind(tag=TAG).error(f"worker shutdown err: {e}")
        finally:
            self._worker_task = None

    # ----------------------------- 工具接口 -----------------------------

    def has_tool(self, name: str) -> bool:
        return any(t.name == name for t in self.tools)

    def get_available_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema,
                },
            }
            for t in self.tools
        ]

    async def call_tool(self, name: str, args: dict):
        """
        转发到 session.call_tool。
        若在 worker 之外的 task 调用，会通过 run_coroutine_threadsafe
        投递到 worker 所在 loop 中执行，保证线程安全。
        """
        if not self.session:  # 尚未就绪
            raise RuntimeError("MCPClient not initialized")

        loop = self._worker_task.get_loop()
        coro = self.session.call_tool(name, args)

        # 在同一个 loop ➜ 直接 await
        if loop is asyncio.get_running_loop():
            return await coro

        # 跨 loop ➜ run_coroutine_threadsafe
        fut: concurrent.futures.Future = asyncio.run_coroutine_threadsafe(coro, loop)
        return await asyncio.wrap_future(fut)

    # ----------------------------- 后台 task -----------------------------

    async def _worker(self):
        """
        单线程协程：
            1. 创建所有异步资源
            2. set_ready → 供外部使用
            3. 等待 shutdown_evt
            4. 自动随 AsyncExitStack 退出而清理资源
        """
        async with AsyncExitStack() as stack:
            try:
                # ---------- 启动后端进程 ----------
                cmd = shutil.which("npx") if self.config["command"] == "npx" else self.config["command"]
                env = {**os.environ, **self.config.get("env", {})}
                params = StdioServerParameters(
                    command=cmd,
                    args=self.config.get("args", []),
                    env=env,
                )
                stdio_r, stdio_w = await stack.enter_async_context(stdio_client(params))

                # ---------- 会话 ----------
                self.session = await stack.enter_async_context(
                    ClientSession(
                        read_stream=stdio_r,
                        write_stream=stdio_w,
                        read_timeout_seconds=timedelta(seconds=15),
                    )
                )
                await self.session.initialize()

                # ---------- 工具 ----------
                self.tools = (await self.session.list_tools()).tools

                # 初始化完成，放行外部
                self._ready_evt.set()

                # ---------- 挂起等待关闭 ----------
                await self._shutdown_evt.wait()

            except Exception as e:
                self.logger.bind(tag=TAG).error(f"worker error: {e}")
                self._ready_evt.set()  # 确保外部不会卡死
                raise
