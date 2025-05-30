import asyncio
import traceback
import queue
import requests
from pathlib import Path
from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import (
    TTSMessageDTO,
    SentenceType,
    ContentType,
    InterfaceType
)
from config.logger import setup_logging
from core.utils import opus_encoder_utils, textUtils

TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.interface_type = InterfaceType.SINGLE_STREAM
        self.access_token = config.get("access_token")
        self.voice = config.get("voice")
        self.api_url = config.get("api_url")
        self.audio_format = config.get("audio_format", "opus")

        # 创建Opus编码器
        self.opus_encoder = opus_encoder_utils.OpusEncoderUtils(
            sample_rate=16000,
            channels=1,
            frame_size_ms=60
        )

        # 添加文本缓冲区
        self.text_buffer = ""
        # 句子结束标点集合
        self.sentence_endings = ("。", "？", "！", "；", ":", ".", "?", "!", ";","……")
        # 逗号类标点（用于第一句话分割）
        self.comma_endings = ("，", "~", "、", ",", "。", ".", "？", "?", "！", "!", "；", ";", "：",)

        # PCM缓冲区
        self.pcm_buffer = bytearray()

    ###################################################################################
    # linkerai单流式TTS重写父类的方法--开始
    ###################################################################################

    def tts_text_priority_thread(self):
        """流式文本处理线程"""
        while not self.conn.stop_event.is_set():
            try:
                message = self.tts_text_queue.get(timeout=1)
                logger.bind(tag=TAG).debug(
                    f"TTS任务｜{message.sentence_type.name}｜{message.content_type.name}"
                )

                if message.sentence_type == SentenceType.FIRST:
                    # 初始化流式状态
                    self.tts_audio_first_sentence = True
                    self.pcm_buffer = bytearray()
                    self.text_buffer = ""  # 重置文本缓冲区

                elif ContentType.TEXT == message.content_type:
                    # 将文本添加到缓冲区
                    self.text_buffer += message.content_detail
                    # 尝试分割并发送完整句子
                    self._process_text_buffer()

                elif ContentType.FILE == message.content_type:
                    # 先处理缓冲区中的剩余文本
                    self._flush_text_buffer()
                    # 处理文件类型
                    if message.content_file and Path(message.content_file).exists():
                        audio_datas = self._process_audio_file(message.content_file)
                        self.tts_audio_queue.put(
                            (SentenceType.MIDDLE, audio_datas, message.content_detail)
                        )

                if message.sentence_type == SentenceType.LAST:
                    # 处理缓冲区中的剩余文本
                    self._flush_text_buffer()
                    # 发送结束帧
                    if self.pcm_buffer:
                        opus_datas = self.wav_to_opus_data_audio_raw(self.pcm_buffer, is_end=True)
                        self.tts_audio_queue.put((SentenceType.MIDDLE, opus_datas, ""))
                        self.pcm_buffer = bytearray()
                    self.tts_audio_queue.put((SentenceType.LAST, [], None))
                    self.text_buffer = ""  # 重置文本缓冲区

            except queue.Empty:
                continue
            except Exception as e:
                logger.bind(tag=TAG).error(
                    f"处理TTS文本失败: {str(e)}, 类型: {type(e).__name__}, 堆栈: {traceback.format_exc()}"
                )

    def _process_text_buffer(self):
        """处理文本缓冲区，分割并发送完整句子"""
        while True:
            # 查找最近的句子结束位置
            end_pos = -1
            for punct in self.sentence_endings:
                pos = self.text_buffer.find(punct)
                if pos != -1 and (end_pos == -1 or pos < end_pos):
                    end_pos = pos

            # 如果是第一句话，也允许在逗号处分隔
            if self.tts_audio_first_sentence and end_pos == -1:
                for punct in self.comma_endings:
                    pos = self.text_buffer.find(punct)
                    if pos != -1 and (end_pos == -1 or pos < end_pos):
                        end_pos = pos

            # 找到分割点
            if end_pos != -1:
                # 提取完整句子
                sentence = self.text_buffer[:end_pos + 1]
                sentence = textUtils.get_string_no_punctuation_or_emoji(sentence)

                if not sentence.strip():  # 检查是否为空文本
                    self.text_buffer = self.text_buffer[end_pos + 1:]
                    continue

                self.text_buffer = self.text_buffer[end_pos + 1:]

                # 发送句子
                future = asyncio.run_coroutine_threadsafe(
                    self.text_to_speak(sentence),
                    loop=self.conn.loop
                )
                future.result()

                # 更新第一句话标志
                if self.tts_audio_first_sentence:
                    self.tts_audio_first_sentence = False
            else:
                break

    def _flush_text_buffer(self):
        """处理缓冲区中剩余的文本"""
        if self.text_buffer:
            clean_text = textUtils.get_string_no_punctuation_or_emoji(self.text_buffer)
            if clean_text.strip():  # 检查是否为空文本
                future = asyncio.run_coroutine_threadsafe(
                    self.text_to_speak(clean_text),
                    loop=self.conn.loop
                )
                future.result()
            self.text_buffer = ""

    async def text_to_speak(self, text):
        # 发送文本
        await self.send_text(text)
        return

    ###################################################################################
    # linkerai单流式TTS重写父类的方法--结束
    ###################################################################################

    async def send_text(self, text: str):
        """流式处理TTS音频"""
        try:
            params = {
                "tts_text": text,
                "spk_id": self.voice,
                "frame_duration": 60,
                "stream": "true",
                "target_sr": 16000,
                "audio_format": self.audio_format,
            }
            headers = {"Authorization": f"Bearer {self.access_token}"}

            with requests.get(self.api_url, params=params, headers=headers, stream=True) as response:
                if response.status_code != 200:
                    logger.error(f"TTS请求失败: {response.status_code}, {response.text}")
                    return

                logger.debug(f"处理TTS文本: {text}")

                # 流式处理音频数据
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        # 实时编码并发送音频帧
                        self.pcm_buffer.extend(chunk)

                # 处理剩余缓冲区数据
                if self.pcm_buffer:
                    opus_datas = self.wav_to_opus_data_audio_raw(self.pcm_buffer, is_end=True)
                    self.tts_audio_queue.put((SentenceType.MIDDLE, opus_datas, text))
                    self.pcm_buffer = bytearray()

        except Exception as e:
            logger.error(f"TTS流式处理异常：{str(e)}")
            raise

    # 保持原有方法
    def wav_to_opus_data_audio_raw(self, raw_data_var, is_end=False):
        opus_datas = self.opus_encoder.encode_pcm_to_opus(raw_data_var, is_end)
        return opus_datas

    async def close(self):
        """资源清理"""
        await super().close()
        if hasattr(self, "opus_encoder"):
            self.opus_encoder.close()
