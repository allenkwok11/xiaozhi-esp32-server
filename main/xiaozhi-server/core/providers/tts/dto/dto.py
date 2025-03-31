from enum import Enum
from typing import Union


class MsgType(Enum):
    # 请求类型
    START_TTS_REQUEST = "START_TTS_REQUEST"
    TTS_TEXT_REQUEST = "TTS_TEXT_REQUEST"
    STOP_TTS_REQUEST = "STOP_TTS_REQUEST"

    # 返回类型
    START_TTS_RESPONSE = "START_TTS_RESPONSE"
    TTS_TEXT_RESPONSE = "TTS_TEXT_RESPONSE"
    STOP_TTS_RESPONSE = "STOP_TTS_RESPONSE"


class SentenceType(Enum):
    # 句子开始
    SENTENCE_START = "SENTENCE_START"
    # 句子结束
    SENTENCE_END = "SENTENCE_END"


class TTSMessageDTO:
    def __init__(self, u_id: str, msg_type: MsgType, content: Union[str, bytes], tts_finish_text=None,
                 sentence_type: SentenceType = None, duration=0):
        if not isinstance(msg_type, MsgType):
            raise ValueError("msg_type must be an instance of MsgType Enum")
        if not isinstance(content, (str, list, bytes)):
            raise ValueError("content must be of type str or bytes")

        # 唯一id，每个合成到合成结束，使用同一个id
        self.u_id = u_id
        self.msg_type = msg_type
        self.sentence_type = sentence_type
        self.content = content
        self.tts_finish_text = tts_finish_text
        self.duration = duration

    def __repr__(self):
        content_preview = self.content if isinstance(self.content, str) else "<binary data>"
        return f"MessageDTO(msg_type={self.msg_type}, content={content_preview})"
