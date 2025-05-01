"""
TTS上报功能已集成到ConnectionHandler类中。

上报功能包括：
1. 每个连接对象拥有自己的上报队列和处理线程
2. 上报线程的生命周期与连接对象绑定
3. 使用ConnectionHandler.enqueue_tts_report方法进行上报

具体实现请参考core/connection.py中的相关代码。
"""

import os
from config.logger import setup_logging
from config.manage_api_client import report

TAG = __name__
logger = setup_logging()

async def report_tts(conn, text, audio_data):
    """执行TTS上报操作
    
    Args:
        conn: 连接对象
        text: 合成文本
        audio_data: 音频二进制数据
    """
    try:
        # 执行上报
        result = await report(
            mac_address=conn.device_id,
            session_id=conn.session_id,
            sort=int(conn.session_open_time),
            chat_type=2,  # TTS类型为2
            content=text,
            audio=audio_data,
            file_extension="wav"
        )
        logger.bind(tag=TAG).info(f"TTS上报成功: {conn.device_id}, {conn.session_id}, 数据大小: {len(audio_data)} 字节")
        return result
    except Exception as e:
        logger.bind(tag=TAG).error(f"TTS上报失败: {e}")
        return None
    finally:
        # 手动清理audio_data引用，帮助垃圾回收
        del audio_data

def enqueue_tts_report(conn, text, file_path):
    """将TTS数据加入上报队列
    
    Args:
        conn: 连接对象
        text: 合成文本
        file_path: TTS音频文件路径
    """
    try:
        # 检查文件是否存在
        if not file_path or not os.path.exists(file_path):
            logger.bind(tag=TAG).error(f"加入TTS上报队列失败: 文件不存在 {file_path}")
            return
            
        # 立即读取文件为二进制数据，因为外部会删除文件
        with open(file_path, 'rb') as f:
            audio_data = f.read()
            
        # 使用连接对象的队列，传入文本和二进制数据而非文件路径
        conn.tts_report_queue.put((text, audio_data))
        
        logger.bind(tag=TAG).info(f"TTS数据已加入上报队列: {conn.device_id}, 文件大小: {len(audio_data)} 字节")
    except Exception as e:
        logger.bind(tag=TAG).error(f"加入TTS上报队列失败: {e}, 文件: {file_path}")
