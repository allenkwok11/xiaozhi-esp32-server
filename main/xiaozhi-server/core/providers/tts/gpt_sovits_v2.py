import os
import uuid
import json
import base64
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
        self.text_lang = config.get("text_lang", "zh")
        self.ref_audio_path = config.get("ref_audio_path")
        self.prompt_text = config.get("prompt_text")
        self.prompt_lang = config.get("prompt_lang", "zh")
        self.top_k = config.get("top_k", 5)
        self.top_p = config.get("top_p", 1)
        self.temperature = config.get("temperature", 1)
        self.text_split_method = config.get("text_split_method", "cut0")
        self.batch_size = config.get("batch_size", 1)
        self.batch_threshold = config.get("batch_threshold", 0.75)
        self.split_bucket = config.get("split_bucket", True)
        self.return_fragment = config.get("return_fragment", False)
        self.speed_factor = config.get("speed_factor", 1.0)
        self.streaming_mode = config.get("streaming_mode", False)
        self.seed = config.get("seed", -1)
        self.parallel_infer = config.get("parallel_infer", True)
        self.repetition_penalty = config.get("repetition_penalty", 1.35)
        self.aux_ref_audio_paths = config.get("aux_ref_audio_paths", [])

    def generate_filename(self, extension=".wav"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        tmp_file = self.generate_filename()
        request_json = {
            "text": text,
            "text_lang": self.text_lang,
            "ref_audio_path": self.ref_audio_path,
            "aux_ref_audio_paths": self.aux_ref_audio_paths,
            "prompt_text": self.prompt_text,
            "prompt_lang": self.prompt_lang,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "text_split_method": self.text_split_method,
            "batch_size": self.batch_size,
            "batch_threshold": self.batch_threshold,
            "split_bucket": self.split_bucket,
            "return_fragment": self.return_fragment,
            "speed_factor": self.speed_factor,
            "streaming_mode": self.streaming_mode,
            "seed": self.seed,
            "parallel_infer": self.parallel_infer,
            "repetition_penalty": self.repetition_penalty
        }

        resp = requests.post(self.url, json=request_json)
        if resp.status_code == 200:
            with open(tmp_file, "wb") as file:
                file.write(resp.content)
        else:
            logger.bind(tag=TAG).error(f"GPT_SoVITS_V2 TTS请求失败: {resp.status_code} - {resp.text}")
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
