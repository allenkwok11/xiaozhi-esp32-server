"""
TTS上报功能已集成到ConnectionHandler类中。

上报功能包括：
1. 每个连接对象拥有自己的上报队列和处理线程
2. 上报线程的生命周期与连接对象绑定
3. 使用ConnectionHandler.enqueue_tts_report方法进行上报

具体实现请参考core/connection.py中的相关代码。
"""

from config.logger import setup_logging
from config.manage_api_client import report

TAG = __name__
logger = setup_logging()


def report_tts(conn, type, text, opus_data):
    """执行TTS上报操作

    Args:
        conn: 连接对象
        type: 上报类型，1为用户，2为智能体
        text: 合成文本
        opus_data: opus音频数据
    """
    try:
        # 执行上报
        report(
            mac_address=conn.device_id,
            session_id=conn.session_id,
            chat_type=type,
            content=text,
            opus_data=opus_data,
        )
    except Exception as e:
        logger.bind(tag=TAG).error(f"TTS上报失败: {e}")


def enqueue_tts_report(conn, type, text, opus_data):
    if not conn.read_config_from_api:
        return
    """将TTS数据加入上报队列

    Args:
        conn: 连接对象
        text: 合成文本
        opus_data: opus音频数据
    """
    try:
        # 使用连接对象的队列，传入文本和二进制数据而非文件路径
        conn.tts_report_queue.put((type, text, opus_data))

        logger.bind(tag=TAG).info(
            f"TTS数据已加入上报队列: {conn.device_id}, 音频大小: {len(opus_data)} "
        )
    except Exception as e:
        logger.bind(tag=TAG).error(f"加入TTS上报队列失败: {text}, {e}")
