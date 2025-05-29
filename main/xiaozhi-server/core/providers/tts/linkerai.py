from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import (
    TTSMessageDTO,
    SentenceType,
    ContentType,
    InterfaceType
)
from config.logger import setup_logging
from core.utils import opus_encoder_utils
import requests

TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.interface_type = InterfaceType.SINGLE_STREAM
        self.access_token = config.get("access_token")
        self.voice = config.get("voice")
        self.api_url = config.get("api_url")

        # 根据配置选择音频格式，优先使用opus
        self.audio_format = config.get("audio_format", "opus")

        # 创建Opus编码器
        self.opus_encoder = opus_encoder_utils.OpusEncoderUtils(
            sample_rate=16000,
            channels=1,
            frame_size_ms=60
        )

    async def text_to_speak(self, text, _):
        """将文本转换为语音（流式）"""
        await self.send_text(self.voice, text)
        return

    async def send_text(self, speaker: str, text: str):
        """向 TTS 服务发送文本并获取音频流"""
        try:
            # 构造请求参数
            params = {
                "tts_text": text,
                "spk_id": self.voice,
                "frame_duration": 60,
                "stream": "true",
                "target_sr": 16000,
                "audio_format": self.audio_format,
            }

            # 构造请求头
            headers = {
                "Authorization": f"Bearer {self.access_token}",
            }

            # 发送流式请求
            response = requests.get(
                self.api_url,
                params=params,
                headers=headers,
                stream=True
            )

            # 检查响应状态
            if response.status_code != 200:
                logger.bind(tag=TAG).error(f"TTS 请求失败: {response.status_code}, {response.text}")
                return

            # 处理音频流
            audio_frames = []
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    if self.audio_format == "pcm":
                        # 将PCM转换为Opus
                        opus_frames = self.opus_encoder.encode_pcm_to_opus(chunk, False)
                        audio_frames.extend(opus_frames)
                    else:
                        # 直接使用Opus帧
                        audio_frames.append(chunk)

            # 将音频帧放入队列
            self.tts_audio_queue.put(
                (SentenceType.MIDDLE, audio_frames, text)
            )

        except Exception as e:
            logger.bind(tag=TAG).error(f"TTS 流式处理异常：{str(e)}")
            raise

    async def close(self):
        """资源清理方法"""
        await super().close()
        if hasattr(self, "opus_encoder"):
            self.opus_encoder.close()
