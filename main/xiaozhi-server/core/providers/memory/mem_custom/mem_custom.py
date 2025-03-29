'''
自定义记忆，可以选择此模块
'''
from ..base import MemoryProviderBase, logger

TAG = __name__

class MemoryProvider(MemoryProviderBase):
    def __init__(self, config):
        super().__init__(config)
      
    async def save_memory(self, msgs):
        logger.bind(tag=TAG).debug("mem_custom mode: Custom memory saving is performed.")
        return None

    async def query_memory(self, query: str)-> str:
        logger.bind(tag=TAG).debug("mem_custom mode: Custom memory query is performed.")
        return ""