from plugins_func.register import register_function, ToolType, ActionResponse, Action
from core.handle.sendAudioHandle import send_stt_message
from core.utils.dialogue import Message
from core.providers.tts.dto.dto import TTSMessageDTO, SentenceType, ContentType
from config.logger import setup_logging
import os
import random
import asyncio

TAG = __name__
logger = setup_logging()

STORY_CACHE = {}

christmas_story_function_desc = {
    "type": "function",
    "function": {
        "name": "play_christmas_story",
        "description": "播放圣诞节故事，适合在节日时为用户讲述温馨的圣诞故事",
        "parameters": {
            "type": "object",
            "properties": {
                "story_name": {
                    "type": "string",
                    "description": "故事名称，如果用户没有指定具体故事则为'random'，指定时返回故事名字",
                }
            },
            "required": ["story_name"],
        },
    },
}

@register_function("play_christmas_story", christmas_story_function_desc, ToolType.SYSTEM_CTL)
def play_christmas_story(conn, story_name: str):
    try:
        story_intent = f"播放圣诞故事 {story_name}" if story_name != "random" else "随机播放圣诞故事"
        
        if not conn.loop.is_running():
            logger.bind(tag=TAG).error("事件循环未运行，无法提交任务")
            return ActionResponse(
                action=Action.RESPONSE, result="系统繁忙", response="请稍后再试"
            )

        # 提交异步任务
        future = asyncio.run_coroutine_threadsafe(
            handle_christmas_story_command(conn, story_intent), conn.loop
        )

        def handle_done(f):
            try:
                f.result()
                logger.bind(tag=TAG).info("故事播放完成")
            except Exception as e:
                logger.bind(tag=TAG).error(f"故事播放失败: {e}")

        future.add_done_callback(handle_done)

        return ActionResponse(
            action=Action.NONE, result="指令已接收", response="正在为您讲述圣诞故事"
        )
    except Exception as e:
        logger.bind(tag=TAG).error(f"处理圣诞故事意图错误: {e}")
        return ActionResponse(
            action=Action.RESPONSE, result=str(e), response="播放故事时出错了"
        )

def initialize_story_handler(conn):
    global STORY_CACHE
    if STORY_CACHE == {}:
        if "christmas_story" in conn.config["plugins"]:
            STORY_CACHE["story_config"] = conn.config["plugins"]["christmas_story"]
            STORY_CACHE["story_dir"] = os.path.abspath(
                STORY_CACHE["story_config"].get("story_dir", "./stories/christmas")
            )
            STORY_CACHE["story_ext"] = STORY_CACHE["story_config"].get(
                "story_ext", (".mp3", ".wav", ".txt")
            )
        else:
            STORY_CACHE["story_dir"] = os.path.abspath("./stories/christmas")
            STORY_CACHE["story_ext"] = (".mp3", ".wav", ".txt")
        
        # 获取故事文件列表
        STORY_CACHE["story_files"] = get_story_files(
            STORY_CACHE["story_dir"], STORY_CACHE["story_ext"]
        )
    return STORY_CACHE

def get_story_files(story_dir, story_ext):
    """获取故事文件列表"""
    story_files = []
    if os.path.exists(story_dir):
        for file in os.listdir(story_dir):
            if any(file.lower().endswith(ext) for ext in story_ext):
                story_files.append(file)
    return story_files

async def handle_christmas_story_command(conn, text):
    """处理圣诞故事播放指令"""
    initialize_story_handler(conn)
    global STORY_CACHE
    
    logger.bind(tag=TAG).debug(f"处理圣诞故事命令: {text}")
    
    if not os.path.exists(STORY_CACHE["story_dir"]):
        logger.bind(tag=TAG).error(f"故事目录不存在: {STORY_CACHE['story_dir']}")
        return
    
    # 这里可以添加故事名称匹配逻辑，类似音乐插件
    await play_christmas_story_file(conn)
    return True

def _get_story_intro_prompt(story_name):
    """生成故事引导语"""
    clean_name = os.path.splitext(story_name)[0]
    prompts = [
        f"让我为您讲述一个温馨的圣诞故事：{clean_name}",
        f"在这个特别的日子里，让我们一起听听：{clean_name}",
        f"圣诞节快到了，让我为您带来：{clean_name}",
        f"请您坐好，我要开始讲述：{clean_name}",
        f"在雪花飞舞的夜晚，让我们聆听：{clean_name}",
    ]
    return random.choice(prompts)

async def play_christmas_story_file(conn, specific_file=None):
    """播放圣诞故事文件"""
    global STORY_CACHE
    
    try:
        if not STORY_CACHE["story_files"]:
            logger.bind(tag=TAG).error("未找到圣诞故事文件")
            return
        
        if specific_file:
            selected_story = specific_file
        else:
            selected_story = random.choice(STORY_CACHE["story_files"])
        
        story_path = os.path.join(STORY_CACHE["story_dir"], selected_story)
        
        if not os.path.exists(story_path):
            logger.bind(tag=TAG).error(f"选定的故事文件不存在: {story_path}")
            return
        
        intro_text = _get_story_intro_prompt(selected_story)
        await send_stt_message(conn, intro_text)
        conn.dialogue.put(Message(role="assistant", content=intro_text))
        
        # 发送TTS消息队列
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
                content_detail=intro_text,
            )
        )
        
        # 如果是文本文件，需要读取内容
        if selected_story.lower().endswith('.txt'):
            with open(story_path, 'r', encoding='utf-8') as f:
                story_content = f.read()
            
            conn.tts.tts_text_queue.put(
                TTSMessageDTO(
                    sentence_id=conn.sentence_id,
                    sentence_type=SentenceType.MIDDLE,
                    content_type=ContentType.TEXT,
                    content_detail=story_content,
                )
            )
        else:
            # 如果是音频文件，直接播放
            conn.tts.tts_text_queue.put(
                TTSMessageDTO(
                    sentence_id=conn.sentence_id,
                    sentence_type=SentenceType.MIDDLE,
                    content_type=ContentType.FILE,
                    content_file=story_path,
                )
            )
        
        conn.tts.tts_text_queue.put(
            TTSMessageDTO(
                sentence_id=conn.sentence_id,
                sentence_type=SentenceType.LAST,
                content_type=ContentType.ACTION,
            )
        )
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"播放圣诞故事失败: {str(e)}")