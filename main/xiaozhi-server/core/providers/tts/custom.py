import os
import uuid
import requests
from pydub import AudioSegment

from config.logger import setup_logging
from datetime import datetime
from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import TTSMessageDTO, MsgType, SentenceType

TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.url = config.get("url")
        self.headers = config.get("headers", {})
        self.params = config.get("params")
        self.format = config.get("format", "wav")
        self.output_file = config.get("output_dir", "tmp/")

    def generate_filename(self):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}.{self.format}")

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        request_params = {}
        tmp_file = self.generate_filename()
        for k, v in self.params.items():
            if isinstance(v, str) and "{prompt_text}" in v:
                v = v.replace("{prompt_text}", text)
            request_params[k] = v

        resp = requests.get(self.url, params=request_params, headers=self.headers)
        if resp.status_code == 200:
            with open(tmp_file, "wb") as file:
                file.write(resp.content)
        else:
            logger.bind(tag=TAG).error(f"Custom TTS请求失败: {resp.status_code} - {resp.text}")
        # 使用 pydub 读取临时文件
        audio = AudioSegment.from_file(tmp_file, format=self.format)
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
