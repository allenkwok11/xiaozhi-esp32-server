import traceback

from config.logger import setup_logging
import json
import asyncio
import time

from core.providers.tts.dto.dto import TTSMessageDTO, SentenceType, MsgType
from core.utils.util import (
    remove_punctuation_and_length,
    get_string_no_punctuation_or_emoji,
)

TAG = __name__
logger = setup_logging()


async def sendAudioMessage(conn, ttsMessageDTO: TTSMessageDTO):
    if ttsMessageDTO.u_id != conn.u_id:
        logger.bind(tag=TAG).info(
            f"msg id:{ttsMessageDTO.u_id},不是当前对话，当前对话id：{conn.u_id}"
        )
        return
    # 发送句子开始消息
    if SentenceType.SENTENCE_START == ttsMessageDTO.sentence_type:
        logger.bind(tag=TAG).info(f"发送第一段语音: {ttsMessageDTO.tts_finish_text}")
        await send_tts_message(conn, "sentence_start", ttsMessageDTO.tts_finish_text)

    # 流控参数优化
    original_frame_duration = 60  # 原始帧时长（毫秒）
    adjusted_frame_duration = int(original_frame_duration * 0.8)  # 缩短20%
    total_frames = len(ttsMessageDTO.content)  # 获取总帧数
    compensation = (
        total_frames * (original_frame_duration - adjusted_frame_duration) / 1000
    )  # 补偿时间（秒）

    start_time = time.perf_counter()
    play_position = 0  # 已播放时长（毫秒）

    for opus_packet in ttsMessageDTO.content:
        if conn.client_abort:
            return

        # 计算带加速因子的预期时间
        expected_time = start_time + (play_position / 1000)
        current_time = time.perf_counter()

        # 流控等待（使用加速后的帧时长）
        delay = expected_time - current_time
        if delay > 0:
            await asyncio.sleep(delay)

        await conn.websocket.send(opus_packet)
        play_position += adjusted_frame_duration  # 使用调整后的帧时长

    # 补偿因加速损失的时长
    if compensation > 0:
        await asyncio.sleep(compensation)
    if SentenceType.SENTENCE_END == ttsMessageDTO.sentence_type:
        logger.bind(tag=TAG).info(f"发送最后一段语音: {ttsMessageDTO.tts_finish_text}")
        await send_tts_message(conn, "sentence_end", ttsMessageDTO.tts_finish_text)

    # 发送结束消息（如果是最后一个文本）
    if conn.llm_finish_task and MsgType.STOP_TTS_RESPONSE == ttsMessageDTO.msg_type:
        await send_tts_message(conn, "stop", None)
        if conn.close_after_chat:
            await conn.close()


async def send_tts_message(conn, state, text=None):
    """发送 TTS 状态消息"""
    message = {"type": "tts", "state": state, "session_id": conn.session_id}
    if text is not None:
        message["text"] = text

    await conn.websocket.send(json.dumps(message))
    if state == "stop":
        conn.clearSpeakStatus()


async def send_stt_message(conn, text):
    """发送 STT 状态消息"""
    stt_text = get_string_no_punctuation_or_emoji(text)
    await conn.websocket.send(
        json.dumps({"type": "stt", "text": stt_text, "session_id": conn.session_id})
    )
    await conn.websocket.send(
        json.dumps(
            {
                "type": "llm",
                "text": "😊",
                "emotion": "happy",
                "session_id": conn.session_id,
            }
        )
    )
    await send_tts_message(conn, "start")
