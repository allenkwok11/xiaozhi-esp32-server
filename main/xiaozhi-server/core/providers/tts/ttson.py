import os
import uuid
import json
import requests
import shutil
from datetime import datetime

from pydub import AudioSegment

from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import TTSMessageDTO, MsgType, SentenceType


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.url = config.get(
            "url",
            "https://u95167-bd74-2aef8085.westx.seetacloud.com:8443/flashsummary/tts?token=",
        )
        if config.get("private_voice"):
            self.voice_id = int(config.get("private_voice"))
        else:
            self.voice_id = int(config.get("voice_id", 1695))
        self.token = config.get("token")
        self.to_lang = config.get("to_lang")
        self.volume_change_dB = int(config.get("volume_change_dB", 0))
        self.speed_factor = int(config.get("speed_factor", 1))
        self.stream = str(config.get("stream", False)).lower() in ("true", "1", "yes")
        self.output_file = config.get("output_dir")
        self.pitch_factor = int(config.get("pitch_factor", 0))
        self.format = config.get("format", "mp3")
        self.emotion = int(config.get("emotion", 1))
        self.header = {"Content-Type": "application/json"}

    def generate_filename(self, extension=".mp3"):
        return os.path.join(
            self.output_file,
            f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}",
        )

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        tmp_file = self.generate_filename()
        url = f"{self.url}{self.token}"
        result = "firefly"
        payload = json.dumps(
            {
                "to_lang": self.to_lang,
                "text": text,
                "emotion": self.emotion,
                "format": self.format,
                "volume_change_dB": self.volume_change_dB,
                "voice_id": self.voice_id,
                "pitch_factor": self.pitch_factor,
                "speed_factor": self.speed_factor,
                "token": self.token,
            }
        )

        resp = requests.request("POST", url, data=payload)
        if resp.status_code != 200:
            return
        resp_json = resp.json()
        try:
            result = (
                resp_json["url"]
                + ":"
                + str(resp_json["port"])
                + "/flashsummary/retrieveFileData?stream=True&token="
                + self.token
                + "&voice_audio_path="
                + resp_json["voice_path"]
            )
        except Exception as e:
            print("error:", e)

        audio_content = requests.get(result)
        with open(tmp_file, "wb") as f:
            f.write(audio_content.content)
            # 使用 pydub 读取临时文件
            audio = AudioSegment.from_file(tmp_file, format="mp3")
            audio = audio.set_channels(1).set_frame_rate(16000)
            opus_datas = self.wav_to_opus_data_audio_raw(audio.raw_data)
            yield TTSMessageDTO(
                u_id=u_id,
                msg_type=MsgType.TTS_TEXT_RESPONSE,
                content=opus_datas,
                tts_finish_text=text,
                sentence_type=SentenceType.SENTENCE_START,
            )
            # 用完后删除临时文件
            try:
                os.remove(tmp_file)
            except FileNotFoundError:
                # 若文件不存在，忽略该异常
                pass
        voice_path = resp_json.get("voice_path")
        des_path = tmp_file
        shutil.move(voice_path, des_path)
