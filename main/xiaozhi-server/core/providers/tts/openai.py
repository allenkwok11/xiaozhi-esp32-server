import os
import uuid
import requests
from datetime import datetime

from pydub import AudioSegment

from core.providers.tts.dto.dto import TTSMessageDTO, MsgType, SentenceType
from core.utils.util import check_model_key
from core.providers.tts.base import TTSProviderBase

class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.api_key = config.get("api_key")
        self.api_url = config.get("api_url", "https://api.openai.com/v1/audio/speech")
        self.model = config.get("model", "tts-1")
        self.voice = config.get("voice", "alloy")
        self.response_format = "wav"
        self.speed = config.get("speed", 1.0)
        self.output_file = config.get("output_dir", "tmp/")
        check_model_key("TTS", self.api_key)

    def generate_filename(self, extension=".wav"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        tmp_file = self.generate_filename()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "input": text,
            "voice": self.voice,
            "response_format": "wav",
            "speed": self.speed
        }
        response = requests.post(self.api_url, json=data, headers=headers)
        if response.status_code == 200:
            with open(tmp_file, "wb") as audio_file:
                audio_file.write(response.content)
        else:
            raise Exception(f"OpenAI TTS请求失败: {response.status_code} - {response.text}")
        # 使用 pydub 读取临时文件
        audio = AudioSegment.from_file(tmp_file, format="wav")
        audio = audio.set_channels(1).set_frame_rate(16000)
        opus_datas = self.wav_to_opus_data_audio_raw(audio.raw_data)
        yield TTSMessageDTO(u_id=u_id, msg_type=MsgType.TTS_TEXT_RESPONSE, content=opus_datas, tts_finish_text=text,
                            sentence_type=SentenceType.SENTENCE_START)
        # 用完后删除临时文件
        try:
            os.remove(tmp_file)
        except FileNotFoundError:
            # 若文件不存在，忽略该异常
            pass
