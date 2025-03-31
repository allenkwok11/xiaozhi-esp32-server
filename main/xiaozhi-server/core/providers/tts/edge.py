import io
import os
import uuid
import edge_tts
from datetime import datetime

from pydub import AudioSegment

from config.logger import setup_logging
from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import TTSMessageDTO, MsgType, SentenceType

TAG = __name__
logger = setup_logging()

class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.voice = config.get("voice")

    def generate_filename(self, extension=".mp3"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        try:
            communicate = edge_tts.Communicate(text, voice=self.voice)  # Use your preferred voice
            tmp_file = self.generate_filename()
            await communicate.save(tmp_file)

            # 使用 pydub 读取临时文件
            audio = AudioSegment.from_file(tmp_file, format="mp3")
            audio = audio.set_channels(1).set_frame_rate(16000)
            opus_datas = self.wav_to_opus_data_audio_raw(audio.raw_data)
            yield TTSMessageDTO(u_id=u_id, msg_type=MsgType.TTS_TEXT_RESPONSE, content=opus_datas, tts_finish_text=text,sentence_type=SentenceType.SENTENCE_START)
            # 用完后删除临时文件
            try:
                os.remove(tmp_file)
            except FileNotFoundError:
                # 若文件不存在，忽略该异常
                pass
        except Exception as e:
            logger.bind(tag=TAG).error(f"TTSProvider text_to_speak error: {e}")
            yield TTSMessageDTO(u_id=u_id, msg_type=MsgType.TTS_TEXT_RESPONSE, content=[], tts_finish_text=text,sentence_type=SentenceType.SENTENCE_START)


