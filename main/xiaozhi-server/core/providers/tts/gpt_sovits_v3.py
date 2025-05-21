import os
import uuid
import requests
from pydub import AudioSegment
from core.utils.util import parse_string_to_list
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
        self.refer_wav_path = config.get("refer_wav_path")
        self.prompt_text = config.get("prompt_text")
        self.prompt_language = config.get("prompt_language")
        self.text_language = config.get("text_language", "audo")

        # 处理空字符串的情况
        top_k = config.get("top_k", "15")
        top_p = config.get("top_p", "1.0")
        temperature = config.get("temperature", "1.0")
        sample_steps = config.get("sample_steps", "32")
        speed = config.get("speed", "1.0")

        self.top_k = int(top_k) if top_k else 15
        self.top_p = float(top_p) if top_p else 1.0
        self.temperature = float(temperature) if temperature else 1.0
        self.sample_steps = int(sample_steps) if sample_steps else 32
        self.speed = float(speed) if speed else 1.0

        self.cut_punc = config.get("cut_punc", "")
        self.inp_refs = parse_string_to_list(config.get("inp_refs"))
        self.if_sr = str(config.get("if_sr", False)).lower() in ("true", "1", "yes")

    def generate_filename(self, extension=".wav"):
        return os.path.join(
            self.output_file,
            f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}",
        )

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        tmp_file = self.generate_filename()
        request_params = {
            "refer_wav_path": self.refer_wav_path,
            "prompt_text": self.prompt_text,
            "prompt_language": self.prompt_language,
            "text": text,
            "text_language": self.text_language,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "cut_punc": self.cut_punc,
            "speed": self.speed,
            "inp_refs": self.inp_refs,
            "sample_steps": self.sample_steps,
            "if_sr": self.if_sr,
        }

        resp = requests.get(self.url, params=request_params)
        if resp.status_code == 200:
            with open(tmp_file, "wb") as file:
                file.write(resp.content)
        else:
            logger.bind(tag=TAG).error(
                f"GPT_SoVITS_V3 TTS请求失败: {resp.status_code} - {resp.text}"
            )
        # 使用 pydub 读取临时文件
        audio = AudioSegment.from_file(tmp_file, format="wav")
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
