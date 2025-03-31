import os
import uuid
import requests
from datetime import datetime

from pydub import AudioSegment

from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import TTSMessageDTO, MsgType, SentenceType


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.model = config.get("model")
        self.access_token = config.get("access_token")
        self.voice = config.get("voice")
        self.response_format = config.get("response_format")
        self.sample_rate = config.get("sample_rate")
        self.speed = config.get("speed")
        self.gain = config.get("gain")

        self.host = "api.siliconflow.cn"
        self.api_url = f"https://{self.host}/v1/audio/speech"

    def generate_filename(self, extension=".wav"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        tmp_file = self.generate_filename()
        request_json = {
            "model": self.model,
            "input": text,
            "voice": self.voice,
            "response_format": self.response_format,
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request("POST", self.api_url, json=request_json, headers=headers)
        data = response.content
        file_to_save = open(tmp_file, "wb")
        file_to_save.write(data)
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
