import json
import time
import asyncio
from aiohttp import web
from config.logger import setup_logging
from core.connection import ConnectionHandler
from core.utils.util import get_local_ip, initialize_modules

TAG = __name__


class SimpleOtaServer:
    def __init__(self, config: dict):
        self.config = config
        self.logger = setup_logging()

    async def start(self):
        server_config = self.config["server"]
        host = server_config.get("ip", "0.0.0.0")
        port = int(server_config.get("ota_port"))

        if port:
            self.logger.bind(tag=TAG).info(
                "Simple OTA Server is running at http://{}:{}/xiaozhi/ota/", get_local_ip(), port
            )
            self.logger.bind(tag=TAG).info(
                "=======上面的地址为最简化安装环境提供OTA基础信息，可用作小智固件的自定义OTA地址======="
            )
            self.logger.bind(tag=TAG).info(
                "如想测试OTA地址请用谷歌浏览器打开test目录下的test_page.html"
            )
            self.logger.bind(tag=TAG).info(
                "=============================================================\n"
            )

            app = web.Application()

            # 添加路由
            app.add_routes([
                web.post("/xiaozhi/ota/", self._handle_ota_request),
                web.options("/xiaozhi/ota/", self._handle_ota_request)
            ])

            # 运行服务
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()

            # 保持服务运行
            while True:
                await asyncio.sleep(3600)  # 每隔 1 小时检查一次

    async def _handle_ota_request(self, request):
        """处理 /xiaozhi/ota/ 的 POST 请求"""
        try:
            data = await request.text()
            self.logger.bind(tag=TAG).debug(f"OTA请求方法: {request.method}")
            self.logger.bind(tag=TAG).debug(f"OTA请求头: {request.headers}")
            self.logger.bind(tag=TAG).debug(f"OTA请求数据: {data}")

            device_id = request.headers.get("device-id", "")
            if device_id:
                self.logger.bind(tag=TAG).info(f"OTA请求设备ID: {device_id}")
            else:
                raise Exception("OTA请求设备ID为空")

            data_json = json.loads(data)

            server_config = self.config["server"]
            host = server_config.get("ip", "0.0.0.0")
            port = int(server_config.get("port", 8000))
            local_ip = get_local_ip()

            # OTA基础信息
            return_json = {
                "server_time":{
                    "timestamp": int(round(time.time() * 1000)),
                    "timezone_offset": server_config.get("timezone_offset", 8) * 60
                },
                "firmware": {
                    "version": data_json["application"].get("version", "1.0.0"),
                    "url": ""
                },
                "websocket":{
                    "url": f"ws://{local_ip}:{port}/xiaozhi/v1/",
                }
            }
            response = web.Response(text=json.dumps(return_json, separators=(',', ':')), content_type="application/json")
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"OTA请求异常: {e}")
            return_json = {"success": False, "message": "request error."}
            response = web.Response(text=json.dumps(return_json, separators=(',', ':')), content_type="application/json")
        finally:
            # 添加header，允许跨域访问
            response.headers["Access-Control-Allow-Headers"] = "client-id, content-type, device-id"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response
