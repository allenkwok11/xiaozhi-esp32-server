import os
import time
import queue
import asyncio
import requests
import traceback
from config.logger import setup_logging
from core.utils.tts import MarkdownCleaner
from core.providers.tts.base import TTSProviderBase
from core.utils import opus_encoder_utils, textUtils
from core.providers.tts.dto.dto import SentenceType, ContentType, InterfaceType

TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.interface_type = InterfaceType.SINGLE_STREAM
        self.access_token = config.get("access_token")
        self.voice = config.get("voice")
        self.api_url = config.get("api_url")
        self.audio_format = "pcm"
        self.before_stop_play_files = []

        # 创建Opus编码器
        self.opus_encoder = opus_encoder_utils.OpusEncoderUtils(
            sample_rate=16000, channels=1, frame_size_ms=60
        )

        # 添加文本缓冲区
        self.text_buffer = ""

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
                if message.sentence_type == SentenceType.FIRST:
                    # 初始化参数
                    self.tts_stop_request = False
                    self.processed_chars = 0
                    self.tts_text_buff = []
                    self.is_first_sentence = True
                    self.tts_audio_first_sentence = True
                    self.before_stop_play_files.clear()
                elif ContentType.TEXT == message.content_type:
                    self.tts_text_buff.append(message.content_detail)
                    segment_text = self._get_segment_text()
                    if segment_text:
                        self.to_tts(segment_text)

                elif ContentType.FILE == message.content_type:
                    self._process_remaining_text()
                    logger.bind(tag=TAG).info(
                        f"添加音频文件到待播放列表: {message.content_file}"
                    )
                    self.before_stop_play_files.append(
                        (message.content_file, message.content_detail)
                    )

                if message.sentence_type == SentenceType.LAST:
                    self._process_remaining_text()

            except queue.Empty:
                continue
            except Exception as e:
                logger.bind(tag=TAG).error(
                    f"处理TTS文本失败: {str(e)}, 类型: {type(e).__name__}, 堆栈: {traceback.format_exc()}"
                )

    def _process_remaining_text(self):
        """处理剩余的文本并生成语音

        Returns:
            bool: 是否成功处理了文本
        """
        full_text = "".join(self.tts_text_buff)
        remaining_text = full_text[self.processed_chars :]
        if remaining_text:
            segment_text = textUtils.get_string_no_punctuation_or_emoji(remaining_text)
            if segment_text:
                self.to_tts(segment_text)
                self.processed_chars += len(full_text)

    def to_tts(self, text):
        try:
            max_repeat_time = 5
            text = MarkdownCleaner.clean_markdown(text)
            try:
                asyncio.run(self.text_to_speak(text, None))
            except Exception as e:
                logger.bind(tag=TAG).warning(
                    f"语音生成失败{5 - max_repeat_time + 1}次: {text}，错误: {e}"
                )
                max_repeat_time -= 1

            if max_repeat_time > 0:
                logger.bind(tag=TAG).info(
                    f"语音生成成功: {text}，重试{5 - max_repeat_time}次"
                )
            else:
                logger.bind(tag=TAG).error(
                    f"语音生成失败: {text}，请检查网络或服务是否正常"
                )
        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to generate TTS file: {e}")
        finally:
            return None

    ###################################################################################
    # linkerai单流式TTS重写父类的方法--结束
    ###################################################################################

    async def text_to_speak(self, text, _):
        """流式处理TTS音频，每句只推送一次音频列表"""
        start_time = time.time()
        logger.info(f"TTS请求: {text}")
        try:
            params = {
                "tts_text": text,
                "spk_id": self.voice,
                "frame_duration": 60,
                "stream": True,
                "target_sr": 16000,
                "audio_format": self.audio_format,
            }
            headers = {"Authorization": f"Bearer {self.access_token}"}

            with requests.get(
                self.api_url, params=params, headers=headers, timeout=5
            ) as response:
                if response.status_code != 200:
                    logger.error(
                        f"TTS请求失败: {response.status_code}, {response.text}"
                    )
                    # 推送空LAST，防止播放端卡死
                    self.tts_audio_queue.put((SentenceType.LAST, [], None))
                    return
                logger.info(f"TTS请求成功: {text}, 耗时: {time.time() - start_time}秒")
                opus_datas = self.wav_to_opus_data_audio_raw(response.content)
                self.tts_audio_queue.put((SentenceType.MIDDLE, opus_datas, text))
        except Exception as e:
            logger.error(f"TTS流式处理异常：{str(e)}")
            # 推送空LAST，防止播放端卡死
            self.tts_audio_queue.put((SentenceType.LAST, [], None))

    # 保持原有方法
    def wav_to_opus_data_audio_raw(self, raw_data_var):
        opus_datas = self.opus_encoder.encode_pcm_to_opus(
            raw_data_var, end_of_stream=True
        )
        return opus_datas

    async def close(self):
        """资源清理"""
        await super().close()
        if hasattr(self, "opus_encoder"):
            self.opus_encoder.close()
