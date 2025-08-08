from config.logger import setup_logging
import urllib.parse
import asyncio
from plugins_func.register import register_function, ToolType, ActionResponse, Action
from core.providers.tts.dto.dto import TTSMessageDTO, SentenceType, ContentType

TAG = __name__

santa_speak_function_desc = {
    "type": "function",
    "function": {
        "name": "santa_speak",
        "description": "Let Santa speak with his jolly personality - Ho ho ho!",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text that Santa should speak",
                }
            },
            "required": ["text"],
        },
    },
}

@register_function("santa_speak", santa_speak_function_desc, ToolType.SYSTEM_CTL)
def santa_speak(conn, text: str):
    try:
        # Check if event loop is running
        if not conn.loop.is_running():
            conn.logger.bind(tag=TAG).error("Event loop not running, cannot submit task")
            return ActionResponse(
                action=Action.RESPONSE, 
                result="System busy", 
                response="Please try again later"
            )

        # Submit async task
        future = asyncio.run_coroutine_threadsafe(
            handle_santa_speech(conn, text), conn.loop
        )

        # Non-blocking callback handling
        def handle_done(f):
            try:
                f.result()
                conn.logger.bind(tag=TAG).info("🎅 Santa finished speaking")
            except Exception as e:
                conn.logger.bind(tag=TAG).error(f"🎅 Santa speech failed: {e}")

        future.add_done_callback(handle_done)

        return ActionResponse(
            action=Action.NONE, 
            result="🎅 Santa will speak", 
            response="Ho ho ho! Santa is preparing to speak!"
        )
    except Exception as e:
        conn.logger.bind(tag=TAG).error(f"🎅 Santa speech error: {e}")
        return ActionResponse(
            action=Action.RESPONSE, 
            result=str(e), 
            response="🎅 Santa had trouble speaking"
        )

async def handle_santa_speech(conn, text):
    """Handle Santa's speech with normal voice but jolly personality"""
    try:
        # Add Santa character to the text
        if not text.lower().startswith('ho ho ho'):
            santa_text = f"Ho ho ho! {text}"
        else:
            santa_text = text
        
        conn.logger.bind(tag=TAG).info(f"🎅 Santa will speak: {santa_text}")
        
        # Use the same TTS queue system as other plugins - no voice changing
        conn.tts.tts_text_queue.put(
            TTSMessageDTO(
                sentence_id=conn.sentence_id,
                sentence_type=SentenceType.FIRST,
                content_type=ContentType.ACTION,
            )
        )
        
        conn.tts.tts_text_queue.put(
            TTSMessageDTO(
                sentence_id=conn.sentence_id,
                sentence_type=SentenceType.MIDDLE,
                content_type=ContentType.TEXT,
                content_detail=santa_text,
            )
        )
        
        conn.tts.tts_text_queue.put(
            TTSMessageDTO(
                sentence_id=conn.sentence_id,
                sentence_type=SentenceType.LAST,
                content_type=ContentType.ACTION,
            )
        )
        
        conn.logger.bind(tag=TAG).info("🎅 Santa speech queued successfully!")
        
    except Exception as e:
        conn.logger.bind(tag=TAG).error(f"🎅 Santa speech handling failed: {str(e)}")
        raise e