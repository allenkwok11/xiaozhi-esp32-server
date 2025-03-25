from abc import ABC, abstractmethod
from typing import List, Dict
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class IntentProviderBase(ABC):
    def __init__(self, config):
        self.config = config
        self.intent_options = config.get("intent_options", {
            "continue_chat": "继续聊天",
            "end_chat": "结束聊天",
            "play_music": "播放音乐",
            "get_weather": "查询天气",
            "get_news": "查询新闻"
        })

    def set_llm(self, llm):
        self.llm = llm
        # 获取模型名称和类型信息
        model_name = getattr(llm, 'model_name', str(llm.__class__.__name__))
        model_type = getattr(llm, 'type', 'unknown')
        # 记录更详细的日志
        logger.bind(tag=TAG).info(f"意图识别设置LLM: {model_name}, 类型: {model_type}")
        # 尝试获取模型基础URL
        base_url = getattr(llm, 'base_url', 'N/A')
        if base_url != 'N/A':
            logger.bind(tag=TAG).debug(f"意图识别LLM基础URL: {base_url}")

    @abstractmethod
    async def detect_intent(self, conn, dialogue_history: List[Dict], text: str) -> str:
        """
        检测用户最后一句话的意图
        Args:
            dialogue_history: 对话历史记录列表，每条记录包含role和content
        Returns:
            返回识别出的意图，格式为:
            - "继续聊天"
            - "结束聊天" 
            - "播放音乐 歌名" 或 "随机播放音乐"
            - "查询天气 地点名" 或 "查询天气 [当前位置]"
        """
        pass
