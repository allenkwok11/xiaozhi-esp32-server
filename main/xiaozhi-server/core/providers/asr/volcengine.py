import time
import io
import wave
import os
from typing import Optional, Tuple, List
import uuid
import websockets
import json
import gzip

import opuslib_next
from core.utils.util import check_model_key
from core.providers.asr.base import ASRProviderBase

from config.logger import setup_logging

TAG = __name__
logger = setup_logging()

PROTOCOL_VERSION = 0b0001
DEFAULT_HEADER_SIZE = 0b0001

# Message Type:
FULL_CLIENT_REQUEST = 0b0001
AUDIO_ONLY_REQUEST = 0b0010
FULL_SERVER_RESPONSE = 0b1001
SERVER_ERROR_RESPONSE = 0b1111

# Message Type Specific Flags
FLAG_NO_SEQUENCE = 0b0000
FLAG_WITH_SEQUENCE = 0b0001
FLAG_LAST_PACKET = 0b0010

# Message Serialization
NO_SERIALIZATION = 0b0000
JSON = 0b0001

# Message Compression
NO_COMPRESSION = 0b0000
GZIP = 0b0001


class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        self.host = config.get("base_host", "openspeech.bytedance.com")
        self.ws_url = f"wss://{self.host}/api/v3/sauc/bigmodel"

        self.appid = config.get("appid")
        self.access_token = config.get("access_token")
        self.resource_id = config.get("resource_id", "volc.bigasr.sauc.duration")
        check_model_key("ASR", self.access_token)

        self.seg_duration = 15000
        # 确保输出目录存在
        self.output_dir = config.get("output_dir")
        os.makedirs(self.output_dir, exist_ok=True)

    def save_audio_to_file(self, opus_data: List[bytes], session_id: str) -> str:
        """将Opus音频数据解码并保存为WAV文件"""
        file_name = f"asr_{session_id}_{uuid.uuid4()}.wav"
        file_path = os.path.join(self.output_dir, file_name)

        decoder = opuslib_next.Decoder(16000, 1)  # 16kHz, 单声道
        pcm_data = []

        for opus_packet in opus_data:
            try:
                pcm_frame = decoder.decode(opus_packet, 960)  # 960 samples = 60ms
                pcm_data.append(pcm_frame)
            except opuslib_next.OpusError as e:
                logger.bind(tag=TAG).error(f"Opus解码错误: {e}", exc_info=True)

        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes = 16-bit
            wf.setframerate(16000)
            wf.writeframes(b"".join(pcm_data))

        return file_path

    @staticmethod
    def _generate_header(message_type=FULL_CLIENT_REQUEST, message_type_specific_flags=FLAG_NO_SEQUENCE,
                         serial_method=JSON, compression_type=GZIP, reserved_data=0x00) -> bytearray:
        """
        protocol_version(4 bits), header_size(4 bits),
        message_type(4 bits), message_type_specific_flags(4 bits)
        serialization_method(4 bits) message_compression(4 bits)
        reserved(8bits) 保留字段
        """
        header = bytearray()
        header.append((PROTOCOL_VERSION << 4) | DEFAULT_HEADER_SIZE)
        header.append((message_type << 4) | message_type_specific_flags)
        header.append((serial_method << 4) | compression_type)
        header.append(reserved_data)
        return header

    @staticmethod
    def _construct_request() -> dict:
        """Construct the request payload."""
        return {
            "user": {
                "uid": str(uuid.uuid4()),
            },
            "audio": {
                "format": "wav",
                "codec": "raw",
                "rate": 16000,
                "bits": 16,
                "channel": 1,
                "language": "zh-CN",
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": False,
                "enable_ddc": False,
                "enable_punc": False,
                "show_utterances": False,
            },
        }

    @staticmethod
    def _parse_response(res):
        """
        protocol_version(4 bits), header_size(4 bits),
        message_type(4 bits), message_type_specific_flags(4 bits)
        serialization_method(4 bits) message_compression(4 bits)
        reserved(8 bits)保留字段
        header_extensions 扩展头(大小等于 8 * 4 * (header_size - 1))
        payload 类似与http 请求体
        """
        protocol_version = res[0] >> 4
        if protocol_version != PROTOCOL_VERSION:
            return None
        header_size = res[0] & 0x0f
        message_type = res[1] >> 4
        message_type_specific_flags = res[1] & 0x0f
        serialization_method = res[2] >> 4
        message_compression = res[2] & 0x0f
        payload = res[header_size * 4:]

        result = {}
        payload_msg = None
        if message_type == FULL_SERVER_RESPONSE:
            if message_type_specific_flags & FLAG_WITH_SEQUENCE:
                # receive frame with sequence
                result['payload_sequence'] = int.from_bytes(payload[:4], "big", signed=True)
                payload = payload[4:]
            if message_type_specific_flags & FLAG_LAST_PACKET:
                # receive last package
                result['is_last_package'] = True
            payload_size = int.from_bytes(payload[:4], "big", signed=True)
            payload_msg = payload[4:4 + payload_size]
        elif message_type == SERVER_ERROR_RESPONSE:
            result['code'] = int.from_bytes(payload[:4], "big", signed=False)
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:8 + payload_size]
        if payload_msg is not None:
            if message_compression == GZIP:
                payload_msg = gzip.decompress(payload_msg)
            if serialization_method == JSON:
                payload_msg = json.loads(str(payload_msg, "utf-8"))
            elif serialization_method != NO_SERIALIZATION:
                payload_msg = str(payload_msg, "utf-8")
            result['payload_msg'] = payload_msg
        return result

    async def _send_request(self, audio_data: List[bytes], segment_size: int) -> Optional[str]:
        """Send request to VolcEngine ASR service."""
        try:
            auth_header = {
                "X-Api-App-Key": self.appid,
                "X-Api-Access-Key": self.access_token,
                "X-Api-Resource-Id": self.resource_id,
                "X-Api-Request-Id": str(uuid.uuid4())
            }
            async with websockets.connect(self.ws_url, additional_headers=auth_header,
                                          max_size=128 * 1024 * 1024) as websocket:
                sequence = 1

                # Send header and metadata
                request_params = self._construct_request()
                payload_bytes = str.encode(json.dumps(request_params))
                payload_bytes = gzip.compress(payload_bytes)
                full_client_request = self._generate_header(message_type_specific_flags=FLAG_WITH_SEQUENCE)
                full_client_request.extend(sequence.to_bytes(4, 'big', signed=True))
                full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
                full_client_request.extend(payload_bytes)  # payload
                await websocket.send(full_client_request)
                res = await websocket.recv()
                result = self._parse_response(res)
                if 'code' in result:
                    logger.bind(tag=TAG).error(f"ASR error: {result['payload_msg']}")
                    return None

                for _, (chunk, last) in enumerate(self.slice_data(audio_data, segment_size), 1):
                    sequence += 1
                    if last:
                        sequence = -sequence  # last package
                        audio_only_request = self._generate_header(
                            message_type=AUDIO_ONLY_REQUEST,
                            message_type_specific_flags=FLAG_WITH_SEQUENCE | FLAG_LAST_PACKET
                        )
                    else:
                        audio_only_request = self._generate_header(
                            message_type=AUDIO_ONLY_REQUEST,
                            message_type_specific_flags=FLAG_WITH_SEQUENCE
                        )
                    audio_only_request.extend(sequence.to_bytes(4, 'big', signed=True))  # sequence
                    payload_bytes = gzip.compress(chunk)
                    audio_only_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
                    audio_only_request.extend(payload_bytes)  # payload
                    # Send audio data
                    await websocket.send(audio_only_request)

                # Receive response
                for _ in range(1, -sequence):
                    response = await websocket.recv()
                    result = self._parse_response(response)
                    if 'code' in result:
                        logger.bind(tag=TAG).error(f"ASR error: {result['payload_msg']}")
                        return None
                    if 'is_last_package' in result and result['is_last_package'] is True:
                        return result.get('payload_msg', {}).get('result', {}).get('text')

                raise Exception("not received last package")

        except Exception as e:
            logger.bind(tag=TAG).error(f"ASR request failed: {e}", exc_info=True)
            return None

    @staticmethod
    def decode_opus(opus_data: List[bytes], session_id: str) -> List[bytes]:
        decoder = opuslib_next.Decoder(16000, 1)  # 16kHz, 单声道
        pcm_data = []

        for opus_packet in opus_data:
            try:
                pcm_frame = decoder.decode(opus_packet, 960)  # 960 samples = 60ms
                pcm_data.append(pcm_frame)
            except opuslib_next.OpusError as e:
                logger.bind(tag=TAG).error(f"Opus解码错误: {e}", exc_info=True)

        return pcm_data

    @staticmethod
    def read_wav_info(data: io.BytesIO = None) -> (int, int, int, int, int):
        with io.BytesIO(data) as _f:
            wave_fp = wave.open(_f, 'rb')
            nchannels, sampwidth, framerate, nframes = wave_fp.getparams()[:4]
            wave_bytes = wave_fp.readframes(nframes)
        return nchannels, sampwidth, framerate, nframes, len(wave_bytes)

    @staticmethod
    def slice_data(data: bytes, chunk_size: int) -> (list, bool):
        """
        slice data
        :param data: wav data
        :param chunk_size: the segment size in one request
        :return: segment data, last flag
        """
        data_len = len(data)
        offset = 0
        while offset + chunk_size < data_len:
            yield data[offset: offset + chunk_size], False
            offset += chunk_size
        else:
            yield data[offset: data_len], True

    async def speech_to_text(self, opus_data: List[bytes], session_id: str) -> Tuple[Optional[str], Optional[str]]:
        """将语音数据转换为文本"""
        try:
            # 合并所有opus数据包
            pcm_data = self.decode_opus(opus_data, session_id)
            combined_pcm_data = b''.join(pcm_data)

            wav_buffer = io.BytesIO()

            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)  # 设置声道数
                wav_file.setsampwidth(2)  # 设置采样宽度
                wav_file.setframerate(16000)  # 设置采样率
                wav_file.writeframes(combined_pcm_data)  # 写入 PCM 数据

            # 获取封装后的 WAV 数据
            wav_data = wav_buffer.getvalue()
            nchannels, sampwidth, framerate, nframes, wav_len = self.read_wav_info(wav_data)
            size_per_sec = nchannels * sampwidth * framerate
            segment_size = int(size_per_sec * self.seg_duration / 1000)

            # 语音识别
            start_time = time.time()
            text = await self._send_request(wav_data, segment_size)
            if text:
                logger.bind(tag=TAG).debug(f"语音识别耗时: {time.time() - start_time:.3f}s | 结果: {text}")
                return text, None
            return "", None

        except Exception as e:
            logger.bind(tag=TAG).error(f"语音识别失败: {e}", exc_info=True)
            return "", None
