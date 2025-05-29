import json
import gzip
import uuid
import asyncio
import websockets
import opuslib_next
from core.providers.asr.base import ASRProviderBase
from config.logger import setup_logging
from core.providers.asr.dto.dto import InterfaceType
import threading

TAG = __name__
logger = setup_logging()

CLIENT_FULL_REQUEST = 0b0001
CLIENT_AUDIO_ONLY_REQUEST = 0b0010
SERVER_FULL_RESPONSE = 0b1001
SERVER_ACK = 0b1011
SERVER_ERROR_RESPONSE = 0b1111
NO_SEQUENCE = 0b0000
NEG_SEQUENCE = 0b0010
JSON_SERIALIZATION = 0b0001
GZIP_COMPRESSION = 0b0001
PROTOCOL_VERSION = 0b0001


class ASRProvider(ASRProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__()
        self.interface_type = InterfaceType.STREAM
        self.config = config
        self.text = ""
        self.max_retries = 3
        self.retry_delay = 2  # 重试延迟秒数
        self.recv_lock = asyncio.Lock()  # 添加接收锁

        self.appid = str(config.get("appid"))
        self.cluster = config.get("cluster")
        self.access_token = config.get("access_token")
        self.boosting_table_name = config.get("boosting_table_name", "")
        self.correct_table_name = config.get("correct_table_name", "")
        self.output_dir = config.get("output_dir", "temp/")
        self.delete_audio_file = delete_audio_file

        self.ws_url = "wss://openspeech.bytedance.com/api/v2/asr"
        self.uid = config.get("uid", "streaming_asr_service")
        self.workflow = config.get(
            "workflow", "audio_in,resample,partition,vad,fe,decode,itn,nlu_punctuate"
        )
        self.result_type = config.get("result_type", "single")
        self.format = config.get("format", "raw")
        self.codec = config.get("codec", "pcm")
        self.rate = config.get("sample_rate", 16000)
        self.language = config.get("language", "zh-CN")
        self.bits = config.get("bits", 16)
        self.channel = config.get("channel", 1)
        self.auth_method = config.get("auth_method", "token")
        self.secret = config.get("secret", "access_secret")
        self.decoder = opuslib_next.Decoder(16000, 1)
        self.asr_ws = None
        self.forward_task = None
        self.conn = None
        self.asr_thread = None

    ###################################################################################
    # 豆包流式ASR重写父类的方法--开始
    ###################################################################################
    async def open_audio_channels(self, conn):
        await super().open_audio_channels(conn)

        retry_count = 0
        while retry_count < self.max_retries:
            try:
                # 确保关闭旧的连接
                if self.asr_ws is not None:
                    try:
                        await self.asr_ws.close()
                    except Exception as e:
                        logger.bind(tag=TAG).warning(f"关闭旧连接时发生错误: {e}")
                    finally:
                        self.asr_ws = None

                headers = self.token_auth() if self.auth_method == "token" else None
                self.asr_ws = await websockets.connect(
                    self.ws_url,
                    additional_headers=headers,
                    max_size=1000000000,
                    ping_interval=None,  # 禁用ping，因为服务器可能不支持
                    ping_timeout=None,
                    close_timeout=10,
                )

                # 发送初始化请求
                request_params = self.construct_request(str(uuid.uuid4()))
                try:
                    payload_bytes = str.encode(json.dumps(request_params))
                    payload_bytes = gzip.compress(payload_bytes)
                    full_client_request = self.generate_header()
                    full_client_request.extend((len(payload_bytes)).to_bytes(4, "big"))
                    full_client_request.extend(payload_bytes)
                    await self.asr_ws.send(full_client_request)
                    logger.bind(tag=TAG).debug(f"发送初始化请求: {request_params}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"发送初始化请求失败: {e}")
                    raise e

                # 等待初始化响应
                try:
                    init_res = await self.asr_ws.recv()
                    result = self.parse_response(init_res)
                    logger.bind(tag=TAG).info(f"ASR服务初始化响应: {result}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"ASR服务初始化失败: {e}")
                    raise e

                # 启动接收ASR结果的异步任务
                asr_priority = threading.Thread(
                    target=self._start_monitor_asr_response_thread, daemon=True
                )
                asr_priority.start()
                return

            except websockets.exceptions.WebSocketException as e:
                retry_count += 1
                if retry_count < self.max_retries:
                    logger.bind(tag=TAG).warning(
                        f"WebSocket连接失败，正在进行第{retry_count}次重试: {e}"
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.bind(tag=TAG).error(
                        f"WebSocket连接失败，已达到最大重试次数: {e}"
                    )
                    raise
            except Exception as e:
                logger.bind(tag=TAG).error(f"WebSocket连接发生未知错误: {e}")
                raise

    async def receive_audio(self, audio, _):
        if not isinstance(audio, bytes):
            return

        try:
            # 解码opus得到PCM数据
            pcm_frame = self.decoder.decode(audio, 960)
            payload = gzip.compress(pcm_frame)
            audio_request = bytearray(self.generate_audio_default_header())
            audio_request.extend(len(payload).to_bytes(4, "big"))
            audio_request.extend(payload)
            if self.asr_ws:
                await self.asr_ws.send(audio_request)
        except Exception as e:
            logger.bind(tag=TAG).error(f"发送音频数据时发生错误: {e}")

    ###################################################################################
    # 豆包流式ASR重写父类的方法--结束
    ###################################################################################

    def construct_request(self, reqid):
        req = {
            "app": {
                "appid": self.appid,
                "cluster": self.cluster,
                "token": self.access_token,
            },
            "user": {"uid": self.uid},
            "request": {
                "reqid": reqid,
                "workflow": self.workflow,
                "show_utterances": True,
                "result_type": self.result_type,
                "sequence": 1,
                "boosting_table_name": self.boosting_table_name,
                "correct_table_name": self.correct_table_name,
            },
            "audio": {
                "format": self.format,
                "codec": self.codec,
                "rate": self.rate,
                "language": self.language,
                "bits": self.bits,
                "channel": self.channel,
            },
        }
        return req

    def token_auth(self):
        return {"Authorization": f"Bearer; {self.access_token}"}

    def generate_header(
        self,
        version=PROTOCOL_VERSION,
        message_type=CLIENT_FULL_REQUEST,
        message_type_specific_flags=NO_SEQUENCE,
        serial_method=JSON_SERIALIZATION,
        compression_type=GZIP_COMPRESSION,
        reserved_data=0x00,
        extension_header: bytes = b"",
    ):
        """
        生成协议头：
         - 第1字节：高4位：协议版本，低4位：头部大小（单位 4 字节）
         - 第2字节：高4位：消息类型，低4位：消息类型特定标志
         - 第3字节：高4位：序列化方式，低4位：压缩方式
         - 第4字节：保留字段
         - 后续：扩展头（如果有）
        """
        header = bytearray()
        header_size = int(len(extension_header) / 4) + 1
        header.append((version << 4) | header_size)
        header.append((message_type << 4) | message_type_specific_flags)
        header.append((serial_method << 4) | compression_type)
        header.append(reserved_data)
        header.extend(extension_header)
        return header

    def generate_full_default_header(self):
        # full client request 默认头
        return self.generate_header(
            version=PROTOCOL_VERSION,
            message_type=CLIENT_FULL_REQUEST,
            message_type_specific_flags=NO_SEQUENCE,
            serial_method=JSON_SERIALIZATION,
            compression_type=GZIP_COMPRESSION,
        )

    def generate_audio_default_header(self):
        # 普通音频片段请求
        return self.generate_header(
            version=PROTOCOL_VERSION,
            message_type=CLIENT_AUDIO_ONLY_REQUEST,
            message_type_specific_flags=NO_SEQUENCE,
            serial_method=JSON_SERIALIZATION,
            compression_type=GZIP_COMPRESSION,
        )

    def generate_last_audio_default_header(self):
        # 最后一个音频片段标志
        return self.generate_header(
            version=PROTOCOL_VERSION,
            message_type=CLIENT_AUDIO_ONLY_REQUEST,
            message_type_specific_flags=NEG_SEQUENCE,  # 用 NEG_SEQUENCE 表示结束
            serial_method=JSON_SERIALIZATION,
            compression_type=GZIP_COMPRESSION,
        )

    def _start_monitor_asr_response_thread(self):
        # 初始化链接
        asyncio.run_coroutine_threadsafe(
            self._forward_asr_results(), loop=self.conn.loop
        )

    async def _forward_asr_results(self):
        try:
            while not self.conn.stop_event.is_set():
                try:
                    if self.asr_ws is None:
                        logger.bind(tag=TAG).info("尝试重新连接ASR服务...")
                        await self.open_audio_channels(self.conn)
                        continue

                    # 使用锁来确保同一时间只有一个协程在接收数据
                    async with self.recv_lock:
                        response = await self.asr_ws.recv()
                        result = self.parse_response(response)
                    # 检查是否需要重连
                    if result.get("need_reconnect", False):
                        logger.bind(tag=TAG).info(
                            "检测到需要重连的错误，准备重新连接..."
                        )
                        if self.asr_ws is not None:
                            try:
                                await self.asr_ws.close()
                            except Exception as e:
                                logger.bind(tag=TAG).warning(
                                    f"关闭旧连接时发生错误: {e}"
                                )
                            finally:
                                self.asr_ws = None
                        continue

                    if "payload_msg" in result:
                        if "result" in result["payload_msg"]:
                            # 检查是否有utterances并且definite为True
                            utterances = result["payload_msg"]["result"][0].get(
                                "utterances", []
                            )
                            for utterance in utterances:
                                if utterance.get("definite", False):
                                    self.text = utterance["text"]
                                    await self.handle_voice_stop(None)
                                    break
                except websockets.ConnectionClosed:
                    logger.bind(tag=TAG).debug("ASR服务连接已关闭，准备重连...")
                    # 确保关闭旧连接
                    if self.asr_ws is not None:
                        try:
                            await self.asr_ws.close()
                        except Exception as e:
                            logger.bind(tag=TAG).warning(f"关闭旧连接时发生错误: {e}")
                        finally:
                            self.asr_ws = None

                    retry_count = 0
                    while (
                        retry_count < self.max_retries
                        and not self.conn.stop_event.is_set()
                    ):
                        try:
                            logger.bind(tag=TAG).info(
                                f"正在进行第{retry_count + 1}次重连尝试..."
                            )
                            await self.open_audio_channels(self.conn)
                            break
                        except Exception as e:
                            retry_count += 1
                            if retry_count < self.max_retries:
                                logger.bind(tag=TAG).warning(
                                    f"重连失败，等待{self.retry_delay}秒后重试: {e}"
                                )
                                await asyncio.sleep(self.retry_delay)
                            else:
                                logger.bind(tag=TAG).error(
                                    f"重连失败，已达到最大重试次数: {e}"
                                )
                                await asyncio.sleep(
                                    self.retry_delay
                                )  # 继续等待，以便后续重试
                except Exception as e:
                    if not self.conn.stop_event.is_set():
                        await asyncio.sleep(2)  # 增加重试延迟
        except Exception as e:
            logger.bind(tag=TAG).error(f"ASR监听线程发生错误: {e}")
            # 确保在发生严重错误时也能继续尝试重连
            if not self.conn.stop_event.is_set():
                await asyncio.sleep(self.retry_delay)
                await self._forward_asr_results()  # 递归重试

    async def speech_to_text(self, opus_data, session_id):
        result = self.text
        self.text = ""  # 清空text
        return result, None

    def parse_response(self, res: bytes) -> dict:
        """
        解析 ASR 服务返回的二进制响应。
        根据协议格式解析头部和 payload，若采用 GZIP 压缩则先解压，再根据 JSON 反序列化。
        """
        protocol_version = res[0] >> 4
        header_size = res[0] & 0x0F
        message_type = res[1] >> 4
        serialization_method = res[2] >> 4
        message_compression = res[2] & 0x0F
        payload = res[header_size * 4 :]
        result = {}
        payload_msg = None
        payload_size = 0

        if message_type == SERVER_FULL_RESPONSE:
            payload_size = int.from_bytes(payload[:4], "big", signed=True)
            payload_msg = payload[4:]
        elif message_type == SERVER_ACK:
            seq = int.from_bytes(payload[:4], "big", signed=True)
            result["seq"] = seq
            if len(payload) >= 8:
                payload_size = int.from_bytes(payload[4:8], "big", signed=False)
                payload_msg = payload[8:]
        elif message_type == SERVER_ERROR_RESPONSE:
            code = int.from_bytes(payload[:4], "big", signed=False)
            result["code"] = code
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:]

        if payload_msg is None:
            return result
        if message_compression == GZIP_COMPRESSION:
            payload_msg = gzip.decompress(payload_msg)
        if serialization_method == JSON_SERIALIZATION:
            payload_msg = json.loads(payload_msg.decode("utf-8"))
        else:
            payload_msg = payload_msg.decode("utf-8")
        result["payload_msg"] = payload_msg
        result["payload_size"] = payload_size

        # 错误码处理
        if "code" in result:
            error_code = result["code"]
            error_message = ""

            if error_code == 1000:
                error_message = "成功"
            elif error_code == 1001:
                error_message = "请求参数无效：请求参数缺失必需字段/字段值无效/重复请求"
            elif error_code == 1002:
                error_message = "无访问权限：token无效/过期/无权访问指定服务"
            elif error_code == 1003:
                error_message = "访问超频：当前appid访问QPS超出设定阈值"
            elif error_code == 1004:
                error_message = "访问超额：当前appid访问次数超出限制"
            elif error_code == 1005:
                error_message = "服务器繁忙：服务过载，无法处理当前请求"
            elif error_code == 1010:
                error_message = "音频过长：音频数据时长超出阈值"
            elif error_code == 1011:
                error_message = "音频过大：音频数据大小超出阈值"
            elif error_code == 1012:
                error_message = "音频格式无效：音频header有误/无法进行音频解码"
            elif error_code == 1013:
                error_message = "音频静音：音频未识别出任何文本结果"
            elif error_code >= 1020 and error_code <= 1022:
                error_message = "识别相关错误：需要重连"
                if error_code == 1020:
                    error_message = "识别等待超时：等待下一包就绪超时"
                elif error_code == 1021:
                    error_message = "识别处理超时：识别处理过程超时"
                elif error_code == 1022:
                    error_message = "识别错误：识别过程中发生错误"
            else:
                error_message = "未知错误：未归类错误"

            logger.bind(tag=TAG).debug(
                f"ASR错误: {error_message} (错误码: {error_code})"
            )

            # 如果是识别相关错误（>=1020），标记需要重连
            if error_code >= 1020:
                result["need_reconnect"] = True

        return result
