from config.logger import setup_logging
import json
import uuid
from core.handle.sendAudioHandle import send_stt_message
from core.handle.helloHandle import checkWakeupWords
from core.utils.util import remove_punctuation_and_length
import re
import asyncio
from loguru import logger

TAG = __name__
logger = setup_logging()


async def handle_user_intent(conn, text):
    # 检查是否有明确的退出命令
    if await check_direct_exit(conn, text):
        return True
    # 检查是否是唤醒词
    if await checkWakeupWords(conn, text):
        return True

    if conn.use_function_call_mode:
        # 使用支持function calling的聊天方法,不再进行意图分析
        return False
    # 使用LLM进行意图分析
    intent_result = await analyze_intent_with_llm(conn, text)
    if not intent_result:
        return False
    # 处理各种意图
    return await process_intent_result(conn, intent_result, text)


async def check_direct_exit(conn, text):
    """检查是否有明确的退出命令"""
    _, text = remove_punctuation_and_length(text)
    cmd_exit = conn.cmd_exit
    for cmd in cmd_exit:
        if text == cmd:
            logger.bind(tag=TAG).info(f"识别到明确的退出命令: {text}")
            await conn.close()
            return True
    return False


async def analyze_intent_with_llm(conn, text):
    """使用LLM分析用户意图"""
    if not hasattr(conn, 'intent') or not conn.intent:
        logger.bind(tag=TAG).warning("意图识别服务未初始化")
        return None

    # 对话历史记录
    dialogue = conn.dialogue
    try:
        intent_result = await conn.intent.detect_intent(conn, dialogue.dialogue, text)
        return intent_result
    except Exception as e:
        logger.bind(tag=TAG).error(f"意图识别失败: {str(e)}")

    return None


async def process_intent_result(conn, intent_result, original_text):
    """处理意图识别结果"""
    try:
        # 尝试将结果解析为JSON
        intent_data = json.loads(intent_result)
        
        # 检查是否有function_call
        if "function_call" in intent_data:
            # 直接从意图识别获取了function_call
            logger.bind(tag=TAG).info(f"检测到function_call格式的意图结果: {intent_data['function_call']['name']}")
            
            function_name = intent_data["function_call"]["name"]
            function_args = intent_data["function_call"]["arguments"]
            
            # 确保参数是字符串格式的JSON
            if isinstance(function_args, dict):
                function_args = json.dumps(function_args)
            
            function_call_data = {
                "name": function_name,
                "id": str(uuid.uuid4().hex),
                "arguments": function_args
            }
            
            # 处理特定类型的函数调用
            if function_name == "get_weather":
                logger.bind(tag=TAG).info(f"识别到天气查询意图")
                # 先发送消息确认
                await send_stt_message(conn, original_text)
                
                # 使用executor执行函数调用和结果处理
                def process_weather_query():
                    # 直接调用函数
                    result = conn.func_handler.handle_llm_function_call(conn, function_call_data)
                    if result:
                        # 获取当前最新的文本索引
                        text_index = conn.tts_last_text_index + 1 if hasattr(conn, 'tts_last_text_index') else 0
                        # 处理函数调用结果
                        conn._handle_function_result(result, function_call_data, text_index)
                
                # 将函数执行放在线程池中
                conn.executor.submit(process_weather_query)
                return True
                
            elif function_name == "play_music":
                logger.bind(tag=TAG).info(f"识别到音乐播放意图")
                # 先发送消息确认
                await send_stt_message(conn, original_text)
                
                # 使用executor执行函数调用和结果处理
                def process_music_query():
                    # 直接调用函数
                    result = conn.func_handler.handle_llm_function_call(conn, function_call_data)
                    if result:
                        # 获取当前最新的文本索引
                        text_index = conn.tts_last_text_index + 1 if hasattr(conn, 'tts_last_text_index') else 0
                        # 处理函数调用结果
                        conn._handle_function_result(result, function_call_data, text_index)
                
                # 将函数执行放在线程池中
                conn.executor.submit(process_music_query)
                return True
                
            elif function_name == "get_news":
                logger.bind(tag=TAG).info(f"识别到新闻查询意图")
                # 先发送消息确认
                await send_stt_message(conn, original_text)
                
                # 使用executor执行函数调用和结果处理
                def process_news_query():
                    # 直接调用函数
                    result = conn.func_handler.handle_llm_function_call(conn, function_call_data)
                    if result:
                        # 获取当前最新的文本索引
                        text_index = conn.tts_last_text_index + 1 if hasattr(conn, 'tts_last_text_index') else 0
                        # 处理函数调用结果
                        conn._handle_function_result(result, function_call_data, text_index)
                
                # 将函数执行放在线程池中
                conn.executor.submit(process_news_query)
                return True
                
            else:
                # 其他类型的函数调用，尝试直接执行
                # 先发送消息确认
                await send_stt_message(conn, original_text)
                
                # 使用executor执行函数调用和结果处理
                def process_function_call():
                    result = conn.func_handler.handle_llm_function_call(conn, function_call_data)
                    if result:
                        # 获取当前最新的文本索引
                        text_index = conn.tts_last_text_index + 1 if hasattr(conn, 'tts_last_text_index') else 0
                        # 处理函数调用结果
                        conn._handle_function_result(result, function_call_data, text_index)
                
                # 将函数执行放在线程池中
                conn.executor.submit(process_function_call)
                return True
            
        # 处理传统意图格式
        elif "intent" in intent_data:
            intent = intent_data["intent"]
            
            # 处理退出意图
            if "结束聊天" in intent:
                logger.bind(tag=TAG).info(f"识别到退出意图: {intent}")
                # 如果是明确的离别意图，发送告别语并关闭连接
                await send_stt_message(conn, original_text)
                conn.executor.submit(conn.chat_and_close, original_text)
                return True
                
            # 其他不需要特殊处理的意图，让常规聊天流程处理
            return False
            
    except json.JSONDecodeError:
        # 如果不是有效的JSON，尝试兼容旧格式
        intent = intent_result
        
        # 处理退出意图
        if "结束聊天" in intent:
            logger.bind(tag=TAG).info(f"识别到退出意图: {intent}")
            # 如果是明确的离别意图，发送告别语并关闭连接
            await send_stt_message(conn, original_text)
            conn.executor.submit(conn.chat_and_close, original_text)
            return True

        # 处理播放音乐意图
        if "播放音乐" in intent:
            logger.bind(tag=TAG).info(f"识别到音乐播放意图: {intent}")
            # 获取歌曲名称
            song_name = extract_text_in_brackets(intent)
            
            # 先发送消息确认
            await send_stt_message(conn, original_text)
            
            # 构造合适的音乐播放函数调用
            function_id = str(uuid.uuid4().hex)
            function_name = "play_music"
            function_arguments = '{ "song_name": ' + (f'"{song_name}"' if song_name else '"random"') + ' }'
            
            function_call_data = {
                "name": function_name,
                "id": function_id,
                "arguments": function_arguments
            }
            
            # 使用executor执行函数调用和结果处理
            def process_music_query():
                # 直接调用函数
                result = conn.func_handler.handle_llm_function_call(conn, function_call_data)
                if result:
                    # 获取当前最新的文本索引
                    text_index = conn.tts_last_text_index + 1 if hasattr(conn, 'tts_last_text_index') else 0
                    # 处理函数调用结果
                    conn._handle_function_result(result, function_call_data, text_index)
            
            # 将函数执行放在线程池中
            conn.executor.submit(process_music_query)
            return True
            
        # 处理查询天气意图
        if "查询天气" in intent:
            logger.bind(tag=TAG).info(f"识别到天气查询意图: {intent}")
            # 获取地点
            location = extract_text_in_brackets(intent)
            
            # 先发送消息确认
            await send_stt_message(conn, original_text)
            
            # 构造合适的天气查询函数调用
            function_id = str(uuid.uuid4().hex)
            function_name = "get_weather"
            function_arguments = '{ "location": ' + (f'"{location}"' if location and location != "当前位置" else 'null') + ', "lang": "zh_CN" }'
            
            function_call_data = {
                "name": function_name,
                "id": function_id,
                "arguments": function_arguments
            }
            
            # 使用executor执行函数调用和结果处理
            def process_weather_query():
                # 直接调用函数
                result = conn.func_handler.handle_llm_function_call(conn, function_call_data)
                if result:
                    # 获取当前最新的文本索引
                    text_index = conn.tts_last_text_index + 1 if hasattr(conn, 'tts_last_text_index') else 0
                    # 处理函数调用结果
                    conn._handle_function_result(result, function_call_data, text_index)
            
            # 将函数执行放在线程池中
            conn.executor.submit(process_weather_query)
            return True
            
        # 处理查询新闻意图
        if "查询新闻" in intent or "播报新闻" in intent or "看新闻" in intent:
            logger.bind(tag=TAG).info(f"识别到新闻查询意图: {intent}")
            # 获取新闻类别
            category = extract_text_in_brackets(intent)
            
            # 先发送消息确认
            await send_stt_message(conn, original_text)
            
            # 构造合适的新闻查询函数调用
            function_id = str(uuid.uuid4().hex)
            function_name = "get_news"
            
            # 判断是否是查询详情
            detail = "详情" in intent or "详细" in intent
            
            # 构造参数JSON字符串
            if detail:
                function_arguments = '{ "detail": true, "lang": "zh_CN" }'
            else:
                function_arguments = '{ "category": ' + (f'"{category}"' if category else 'null') + ', "detail": false, "lang": "zh_CN" }'
            
            function_call_data = {
                "name": function_name,
                "id": function_id,
                "arguments": function_arguments
            }
            
            # 使用executor执行函数调用和结果处理
            def process_news_query():
                # 直接调用函数
                result = conn.func_handler.handle_llm_function_call(conn, function_call_data)
                if result:
                    # 获取当前最新的文本索引
                    text_index = conn.tts_last_text_index + 1 if hasattr(conn, 'tts_last_text_index') else 0
                    # 处理函数调用结果
                    conn._handle_function_result(result, function_call_data, text_index)
            
            # 将函数执行放在线程池中
            conn.executor.submit(process_news_query)
            return True
    except Exception as e:
        logger.bind(tag=TAG).error(f"处理意图结果时出错: {e}")

    # 默认返回False，表示继续常规聊天流程
    return False


def extract_text_in_brackets(s):
    """
    从字符串中提取中括号内的文字

    :param s: 输入字符串
    :return: 中括号内的文字，如果不存在则返回空字符串
    """
    left_bracket_index = s.find('[')
    right_bracket_index = s.find(']')

    if left_bracket_index != -1 and right_bracket_index != -1 and left_bracket_index < right_bracket_index:
        return s[left_bracket_index + 1:right_bracket_index]
    else:
        return ""
