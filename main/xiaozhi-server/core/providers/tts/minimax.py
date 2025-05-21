import os
import uuid
import json
import requests
from core.utils.util import parse_string_to_list
from datetime import datetime
from pydub import AudioSegment
from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import TTSMessageDTO, MsgType, SentenceType


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.group_id = config.get("group_id")
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        if config.get("private_voice"):
            self.voice_id = config.get("private_voice")
        else:
            self.voice_id = config.get("voice_id")

        default_voice_setting = {
            "voice_id": "female-shaonv",
            "speed": 1,
            "vol": 1,
            "pitch": 0,
            "emotion": "happy",
        }
        default_pronunciation_dict = {"tone": ["处理/(chu3)(li3)", "危险/dangerous"]}
        defult_audio_setting = {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        }
        self.voice_setting = {
            **default_voice_setting,
            **config.get("voice_setting", {}),
        }
        self.pronunciation_dict = {
            **default_pronunciation_dict,
            **config.get("pronunciation_dict", {}),
        }
        self.audio_setting = {**defult_audio_setting, **config.get("audio_setting", {})}
        self.timber_weights = parse_string_to_list(config.get("timber_weights"))

        if self.voice_id:
            self.voice_setting["voice_id"] = self.voice_id

        self.host = "api.minimax.chat"
        self.api_url = f"https://{self.host}/v1/t2a_v2?GroupId={self.group_id}"
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def generate_filename(self, extension=".mp3"):
        return os.path.join(
            self.output_file,
            f"tts-{__name__}{datetime.now().date()}@{uuid.uuid4().hex}{extension}",
        )

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        tmp_file = self.generate_filename()
        request_json = {
            "model": self.model,
            "text": text,
            "stream": False,
            "voice_setting": self.voice_setting,
            "pronunciation_dict": self.pronunciation_dict,
            "audio_setting": self.audio_setting,
        }

        if type(self.timber_weights) is list and len(self.timber_weights) > 0:
            request_json["timber_weights"] = self.timber_weights
            request_json["voice_setting"]["voice_id"] = ""

        try:
            resp = requests.post(
                self.api_url, json.dumps(request_json), headers=self.header
            )
            # 检查返回请求数据的status_code是否为0
            if resp.json()["base_resp"]["status_code"] == 0:
                data = resp.json()["data"]["audio"]
                file_to_save = open(tmp_file, "wb")
                file_to_save.write(bytes.fromhex(data))
            else:
                raise Exception(
                    f"{__name__} status_code: {resp.status_code} response: {resp.content}"
                )
        except Exception as e:
            raise Exception(f"{__name__} error: {e}")
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
