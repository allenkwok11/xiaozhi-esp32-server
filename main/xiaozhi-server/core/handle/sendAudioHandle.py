import json
import asyncio
import time
from core.providers.tts.dto.dto import SentenceType
from core.utils.util import get_string_no_punctuation_or_emoji, analyze_emotion, parse_llm_response_with_emotion
from core.utils.emotion_manager import emotion_manager
from loguru import logger

TAG = __name__

# Emoji mapping is now handled by emotion_manager
# Remove hardcoded emoji_map and use emotion_manager.get_emoji() instead


async def sendAudioMessage(conn, sentenceType, audios, text):
    # 发送句子开始消息
    conn.logger.bind(tag=TAG).info(f"sending audio message: {sentenceType}, {text}")
    
    # Always parse and clean the text, regardless of emotion detection method
    original_text = text
    clean_text = text
    llm_emotion = None
    
    if text is not None:
        # Parse LLM response to extract emotion and clean text
        clean_text, llm_emotion = parse_llm_response_with_emotion(text)
        
        # Debug logging to see what's happening with text cleaning
        if clean_text != original_text:
            conn.logger.bind(tag=TAG).info(f"🧹 Text cleaned: '{original_text}' -> '{clean_text}'")
        else:
            conn.logger.bind(tag=TAG).info(f"🧹 No cleaning needed: '{original_text}'")
            
        # Emotion detection: LLM emotion tags take priority over keyword analysis
        if llm_emotion and llm_emotion in emotion_manager.get_emotion_list():
            emotion = llm_emotion
            conn.logger.bind(tag=TAG).info(f"✅ Robot expressing LLM-tagged emotion: '{emotion}' (from response tag)")
        else:
            # Fallback to keyword-based analysis (using original text for analysis)
            emotion = analyze_emotion(original_text)
            conn.logger.bind(tag=TAG).info(f"🔄 Robot expressing keyword-based emotion: '{emotion}' (from keyword analysis)")
        
        # Get emoji from emotion manager
        emoji = emotion_manager.get_emoji(emotion)
        conn.logger.bind(tag=TAG).info(f"🎭 Emotion '{emotion}' mapped to emoji: {emoji}")
        
        await conn.websocket.send(
            json.dumps(
                {
                    "type": "llm",
                    "text": emoji,
                    "emotion": emotion,
                    "session_id": conn.session_id,
                }
            )
        )
    
    # Always use clean_text for TTS operations to avoid emotion tags being spoken
    pre_buffer = False
    if conn.tts.tts_audio_first_sentence and clean_text is not None:
        conn.logger.bind(tag=TAG).info(f"sending first audio: {clean_text}")
        conn.tts.tts_audio_first_sentence = False
        pre_buffer = True

    # Debug logging for TTS calls
    conn.logger.bind(tag=TAG).info(f"🔊 TTS sentence_start with text: '{clean_text}'")
    await send_tts_message(conn, "sentence_start", clean_text)

    await sendAudio(conn, audios, pre_buffer)

    conn.logger.bind(tag=TAG).info(f"🔊 TTS sentence_end with text: '{clean_text}'")
    await send_tts_message(conn, "sentence_end", clean_text)

    # 发送结束消息（如果是最后一个文本）
    if conn.llm_finish_task and sentenceType == SentenceType.LAST:
        await send_tts_message(conn, "stop", None)
        conn.client_is_speaking = False
        if conn.close_after_chat:
            await conn.close()


# 播放音频
async def sendAudio(conn, audios, pre_buffer=True):
    if audios is None or len(audios) == 0:
        return
    # 流控参数优化
    frame_duration = 60  # 帧时长（毫秒），匹配 Opus 编码
    start_time = time.perf_counter()
    play_position = 0
    last_reset_time = time.perf_counter()  # 记录最后的重置时间

    # 仅当第一句话时执行预缓冲
    if pre_buffer:
        pre_buffer_frames = min(3, len(audios))
        for i in range(pre_buffer_frames):
            await conn.websocket.send(audios[i])
        remaining_audios = audios[pre_buffer_frames:]
    else:
        remaining_audios = audios

    # 播放剩余音频帧
    for opus_packet in remaining_audios:
        if conn.client_abort:
            break

        # 每分钟重置一次计时器
        if time.perf_counter() - last_reset_time > 60:
            await conn.reset_timeout()
            last_reset_time = time.perf_counter()

        # 计算预期发送时间
        expected_time = start_time + (play_position / 1000)
        current_time = time.perf_counter()
        delay = expected_time - current_time
        if delay > 0:
            await asyncio.sleep(delay)

        await conn.websocket.send(opus_packet)

        play_position += frame_duration


async def send_tts_message(conn, state, text=None):
    """发送 TTS 状态消息"""
    message = {"type": "tts", "state": state, "session_id": conn.session_id}
    if text is not None:
        message["text"] = text

    # TTS播放结束
    if state == "stop":
        # 播放提示音
        tts_notify = conn.config.get("enable_stop_tts_notify", False)
        if tts_notify:
            stop_tts_notify_voice = conn.config.get(
                "stop_tts_notify_voice", "config/assets/tts_notify.mp3"
            )
            audios, _ = conn.tts.audio_to_opus_data(stop_tts_notify_voice)
            await sendAudio(conn, audios)
        # 清除服务端讲话状态
        conn.clearSpeakStatus()

    # 发送消息到客户端
    await conn.websocket.send(json.dumps(message))


async def send_stt_message(conn, text):
    end_prompt_str = conn.config.get("end_prompt", {}).get("prompt")
    if end_prompt_str and end_prompt_str == text:
        await send_tts_message(conn, "start")
        return

    """发送 STT 状态消息"""
    stt_text = get_string_no_punctuation_or_emoji(text)
    await conn.websocket.send(
        json.dumps({"type": "stt", "text": stt_text, "session_id": conn.session_id})
    )
    conn.client_is_speaking = True
    await send_tts_message(conn, "start")
