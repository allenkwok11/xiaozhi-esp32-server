from typing import List, Dict
from ..base import IntentProviderBase
from plugins_func.functions.play_music import initialize_music_handler
from config.logger import setup_logging
import re
import json
import hashlib
import time

TAG = __name__
logger = setup_logging()


class IntentProvider(IntentProviderBase):
    def __init__(self, config):
        super().__init__(config)
        self.llm = None
        self.promot = self.get_intent_system_prompt()
        # 添加缓存管理
        self.intent_cache = {}  # 缓存意图识别结果
        self.cache_expiry = 600  # 缓存有效期10分钟
        self.cache_max_size = 100  # 最多缓存100个意图
        self.common_patterns = {
            "天气": '{\"function_call\": {\"name\": \"get_weather\", \"arguments\": {\"location\": null, \"lang\": \"zh_CN\"}}}',
            "新闻": '{\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"category\": null, \"detail\": false, \"lang\": \"zh_CN\"}}}',
            "财经新闻": '{\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"category\": \"财经\", \"detail\": false, \"lang\": \"zh_CN\"}}}',
            "国际新闻": '{\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"category\": \"国际\", \"detail\": false, \"lang\": \"zh_CN\"}}}',
            "社会新闻": '{\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"category\": \"社会\", \"detail\": false, \"lang\": \"zh_CN\"}}}',
            "详细介绍": '{\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"detail\": true, \"lang\": \"zh_CN\"}}}',
            "详情": '{\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"detail\": true, \"lang\": \"zh_CN\"}}}',
            "再见": '{\"intent\": \"结束聊天\"}',
            "结束": '{\"intent\": \"结束聊天\"}',
            "拜拜": '{\"intent\": \"结束聊天\"}',
            "播放音乐": '{\"function_call\": {\"name\": \"play_music\", \"arguments\": {\"song_name\": \"random\"}}}'
        }

    def get_intent_system_prompt(self) -> str:
        """
        根据配置的意图选项动态生成系统提示词
        Returns:
            格式化后的系统提示词
        """
        intent_list = []

        """
        "continue_chat":    "1.继续聊天, 除了播放音乐和结束聊天的时候的选项, 比如日常的聊天和问候, 对话等",
        "end_chat":         "2.结束聊天, 用户发来如再见之类的表示结束的话, 不想再进行对话的时候",
        "play_music":       "3.播放音乐, 用户希望你可以播放音乐, 只用于播放音乐的意图",
        "get_weather":      "4.查询天气, 用户希望查询某个地点的天气情况"
        "get_news":         "5.查询新闻, 用户希望查询最新新闻或特定类型的新闻"
        """
        for key, value in self.intent_options.items():
            if key == "play_music":
                intent_list.append("3.播放音乐, 用户希望你可以播放音乐, 只用于播放音乐的意图")
            elif key == "end_chat":
                intent_list.append("2.结束聊天, 用户发来如再见之类的表示结束的话, 不想再进行对话的时候")
            elif key == "continue_chat":
                intent_list.append("1.继续聊天, 除了播放音乐和结束聊天的时候的选项, 比如日常的聊天和问候, 对话等")
            elif key == "get_weather":
                intent_list.append("4.查询天气, 用户希望查询某个地点的天气情况")
            elif key == "get_news":
                intent_list.append("5.查询新闻, 用户希望查询最新新闻或特定类型的新闻")
            else:
                intent_list.append(value)

        prompt = (
            "你是一个意图识别助手。请分析用户的最后一句话，判断用户意图属于以下哪一类：\n"
            "<start>"
            f"{', '.join(intent_list)}"
            "<end>\n"
            "处理步骤:"
            "1. 思考意图类型"
            "2. 继续聊天和结束聊天意图: 返回intent格式"
            "3. 播放音乐意图: 分析歌名，生成function_call格式"
            "4. 查询天气意图: 分析地点，生成function_call格式"
            "5. 查询新闻意图: 分析新闻类别，生成function_call格式"
            "\n\n"
            "返回格式示例：\n"
            "1. 继续聊天意图: {\"intent\": \"继续聊天\"}\n"
            "2. 结束聊天意图: {\"intent\": \"结束聊天\"}\n"
            "3. 播放音乐意图: {\"function_call\": {\"name\": \"play_music\", \"arguments\": {\"song_name\": \"音乐名称\"}}}\n"
            "4. 查询天气意图: {\"function_call\": {\"name\": \"get_weather\", \"arguments\": {\"location\": \"地点名称\", \"lang\": \"zh_CN\"}}}\n"
            "5. 查询新闻意图: {\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"category\": \"新闻类别\", \"detail\": false, \"lang\": \"zh_CN\"}}}\n"
            "\n"
            "注意:\n"
            "- 播放音乐：无歌名时，song_name设为\"random\"\n"
            "- 查询天气：无地点时，location设为null\n"
            "- 查询新闻：无类别时，category设为null；查询详情时，detail设为true\n"
            "- 只返回纯JSON，不要任何其他内容\n"
            "\n"
            "示例分析:\n"
            "```\n"
            "用户: 你今天怎么样?\n"
            "返回: {\"intent\": \"继续聊天\"}\n"
            "```\n"
            "```\n"
            "用户: 我们明天再聊吧\n"
            "返回: {\"intent\": \"结束聊天\"}\n"
            "```\n"
            "```\n"
            "用户: 播放中秋月\n"
            "返回: {\"function_call\": {\"name\": \"play_music\", \"arguments\": {\"song_name\": \"中秋月\"}}}\n"
            "```\n"
            "```\n"
            "用户: 北京天气怎么样\n"
            "返回: {\"function_call\": {\"name\": \"get_weather\", \"arguments\": {\"location\": \"北京\", \"lang\": \"zh_CN\"}}}\n"
            "```\n"
            "```\n"
            "用户: 今天天气怎么样\n"
            "返回: {\"function_call\": {\"name\": \"get_weather\", \"arguments\": {\"location\": null, \"lang\": \"zh_CN\"}}}\n"
            "```\n"
            "```\n"
            "用户: 播报财经新闻\n"
            "返回: {\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"category\": \"财经\", \"detail\": false, \"lang\": \"zh_CN\"}}}\n"
            "```\n"
            "```\n"
            "用户: 有什么最新新闻\n"
            "返回: {\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"category\": null, \"detail\": false, \"lang\": \"zh_CN\"}}}\n"
            "```\n"
            "```\n"
            "用户: 详细介绍一下这条新闻\n"
            "返回: {\"function_call\": {\"name\": \"get_news\", \"arguments\": {\"detail\": true, \"lang\": \"zh_CN\"}}}\n"
            "```\n"
            "可用的音乐名称:\n"
        )
        return prompt
        
    def clean_cache(self):
        """清理过期缓存"""
        now = time.time()
        # 找出过期键
        expired_keys = [k for k, v in self.intent_cache.items() if now - v['timestamp'] > self.cache_expiry]
        for key in expired_keys:
            del self.intent_cache[key]
            
        # 如果缓存太大，移除最旧的条目
        if len(self.intent_cache) > self.cache_max_size:
            # 按时间戳排序并保留最新的条目
            sorted_items = sorted(self.intent_cache.items(), key=lambda x: x[1]['timestamp'])
            for key, _ in sorted_items[:len(sorted_items) - self.cache_max_size]:
                del self.intent_cache[key]

    def check_pattern_match(self, text):
        """检查文本是否匹配常见模式，并提取关键信息"""
        # 城市+天气的特殊模式匹配
        city_weather_pattern = re.search(r'([^\s,，。？！]+)天气', text)
        if city_weather_pattern:
            city = city_weather_pattern.group(1)
            # 排除可能的误匹配，如"今天天气"、"明天天气"、"现在天气"等
            if city not in ["今天", "今日", "明天", "现在", "当前", "未来", "明日", "这两天", "近期"]:
                logger.bind(tag=TAG).info(f"提取到城市名: {city}")
                # 返回包含城市名的function_call
                return f'{{\"function_call\": {{\"name\": \"get_weather\", \"arguments\": {{\"location\": \"{city}\", \"lang\": \"zh_CN\"}}}}}}'
        
        # 普通模式匹配
        for pattern, intent in self.common_patterns.items():
            if pattern in text:
                return intent
                
        return None

    async def detect_intent(self, conn, dialogue_history: List[Dict], text: str) -> str:
        if not self.llm:
            raise ValueError("LLM provider not set")
            
        # 记录整体开始时间
        total_start_time = time.time()
            
        # 打印使用的模型信息
        model_info = getattr(self.llm, 'model_name', str(self.llm.__class__.__name__))
        logger.bind(tag=TAG).info(f"使用意图识别模型: {model_info}")
            
        # 先尝试简单的模式匹配
        pattern_match = self.check_pattern_match(text)
        if pattern_match:
            pattern_time = time.time() - total_start_time
            logger.bind(tag=TAG).info(f"模式匹配成功: {text} -> {pattern_match}, 耗时: {pattern_time:.4f}秒")
            return pattern_match
            
        # 计算缓存键
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        # 检查缓存
        if cache_key in self.intent_cache:
            cache_entry = self.intent_cache[cache_key]
            # 检查缓存是否过期
            if time.time() - cache_entry['timestamp'] <= self.cache_expiry:
                cache_time = time.time() - total_start_time
                logger.bind(tag=TAG).info(f"使用缓存的意图: {cache_key} -> {cache_entry['intent']}, 耗时: {cache_time:.4f}秒")
                return cache_entry['intent']
                
        # 清理缓存
        self.clean_cache()

        # 构建用户最后一句话的提示
        msgStr = ""

        # 只使用最后两句即可
        if len(dialogue_history) >= 2:
            # 保证最少有两句话的时候处理
            msgStr += f"{dialogue_history[-2].role}: {dialogue_history[-2].content}\n"
        msgStr += f"{dialogue_history[-1].role}: {dialogue_history[-1].content}\n"

        msgStr += f"User: {text}\n"
        user_prompt = f"当前的对话如下：\n{msgStr}"
        music_config = initialize_music_handler(conn)
        music_file_names = music_config["music_file_names"]
        prompt_music = f"{self.promot}\n<start>{music_file_names}\n<end>"
        logger.bind(tag=TAG).debug(f"User prompt: {prompt_music}")
        
        # 记录预处理完成时间
        preprocess_time = time.time() - total_start_time
        logger.bind(tag=TAG).debug(f"意图识别预处理耗时: {preprocess_time:.4f}秒")
        
        # 使用LLM进行意图识别
        llm_start_time = time.time()
        logger.bind(tag=TAG).info(f"开始LLM意图识别调用, 模型: {model_info}")
        
        intent = self.llm.response_no_stream(
            system_prompt=prompt_music,
            user_prompt=user_prompt
        )
        
        # 记录LLM调用完成时间
        llm_time = time.time() - llm_start_time
        logger.bind(tag=TAG).info(f"LLM意图识别完成, 模型: {model_info}, 调用耗时: {llm_time:.4f}秒")
        
        # 记录后处理开始时间
        postprocess_start_time = time.time()
        
        # 清理和解析响应
        intent = intent.strip()
        # 尝试提取JSON部分
        match = re.search(r'\{.*\}', intent, re.DOTALL)
        if match:
            intent = match.group(0)
        
        # 记录总处理时间
        total_time = time.time() - total_start_time
        logger.bind(tag=TAG).info(f"【意图识别性能】模型: {model_info}, 总耗时: {total_time:.4f}秒, LLM调用: {llm_time:.4f}秒, 查询: '{text[:20]}...'")
        
        # 尝试解析为JSON
        try:
            intent_data = json.loads(intent)
            # 如果包含function_call，则格式化为适合处理的格式
            if "function_call" in intent_data:
                function_data = intent_data["function_call"]
                function_name = function_data.get("name")
                function_args = function_data.get("arguments", {})
                
                # 记录识别到的function call
                logger.bind(tag=TAG).info(f"识别到function call: {function_name}, 参数: {function_args}")
                
                # 添加到缓存
                self.intent_cache[cache_key] = {
                    'intent': intent,
                    'timestamp': time.time()
                }
                
                # 后处理时间
                postprocess_time = time.time() - postprocess_start_time
                logger.bind(tag=TAG).debug(f"意图后处理耗时: {postprocess_time:.4f}秒")
                
                # 确保返回完全序列化的JSON字符串
                return intent
            else:
                # 添加到缓存
                self.intent_cache[cache_key] = {
                    'intent': intent,
                    'timestamp': time.time()
                }
                
                # 后处理时间
                postprocess_time = time.time() - postprocess_start_time
                logger.bind(tag=TAG).debug(f"意图后处理耗时: {postprocess_time:.4f}秒")
                
                # 返回普通意图
                return intent
        except json.JSONDecodeError:
            # 后处理时间
            postprocess_time = time.time() - postprocess_start_time
            logger.bind(tag=TAG).error(f"无法解析意图JSON: {intent}, 后处理耗时: {postprocess_time:.4f}秒")
            # 如果解析失败，默认返回继续聊天意图
            return "{\"intent\": \"继续聊天\"}"
