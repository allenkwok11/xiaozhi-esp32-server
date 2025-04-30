"""
ASR上报功能已集成到ConnectionHandler类中。

上报功能包括：
1. 每个连接对象拥有自己的上报队列和处理线程
2. 上报线程的生命周期与连接对象绑定
3. 使用ConnectionHandler.enqueue_asr_report方法进行上报

具体实现请参考core/connection.py中的相关代码。
"""

import os
from config.logger import setup_logging
from config.manage_api_client import report

TAG = __name__
logger = setup_logging()

async def report_asr(conn, text, file_path):
    """执行ASR上报操作
    
    Args:
        conn: 连接对象
        text: 识别文本
        file_path: 音频文件路径（可以为None或空字符串，表示纯文本上报）
    """
    audio_data = None
    try:
        # 处理无音频的纯文本上报
        if not file_path or not os.path.exists(file_path):
            # 纯文本上报时使用空音频数据
            result = await report(
                mac_address=conn.device_id,
                session_id=conn.session_id,
                sort=int(conn.session_open_time),
                chat_type=1,  # ASR类型为1
                content=text,
                audio=b'',  # 空音频数据
                file_extension="wav"
            )
            logger.bind(tag=TAG).info(f"纯文本上报成功: {conn.device_id}, {conn.session_id}")
        else:
            # 读取文件为二进制数据
            with open(file_path, 'rb') as f:
                audio_data = f.read()
                
            # 正常ASR上报（带音频）
            result = await report(
                mac_address=conn.device_id,
                session_id=conn.session_id,
                sort=int(conn.session_open_time),
                chat_type=1,  # ASR类型为1
                content=text,
                audio=audio_data,
                file_extension="wav"
            )
            logger.bind(tag=TAG).info(f"ASR上报成功: {conn.device_id}, {conn.session_id}，文件: {file_path}")
        
        return result
    except Exception as e:
        logger.bind(tag=TAG).error(f"ASR上报失败: {e}")
        return None
    finally:
        # 清理资源
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.bind(tag=TAG).debug(f"ASR上报后删除文件: {file_path}")
            except Exception as e:
                logger.bind(tag=TAG).error(f"ASR上报后删除文件失败: {e}")
        
        # 手动清理audio_data
        if audio_data:
            del audio_data

def enqueue_asr_report(conn, text, audio):
    """将ASR数据加入上报队列
    
    Args:
        conn: 连接对象
        text: 识别文本
        audio: 音频数据（可以为空列表，表示纯文本上报）
    """
    try:
        if not audio or len(audio) == 0:
            # 纯文本上报，不需要保存文件
            file_path = None
        else:
            # 保存音频数据到文件
            file_path = conn.asr.save_audio_to_file(audio, conn.session_id)
        
        # 使用连接对象的队列，传入文件路径
        conn.asr_report_queue.put((text, file_path))
        
        if not audio or len(audio) == 0:
            logger.bind(tag=TAG).info(f"纯文本数据已加入上报队列: {conn.device_id}, {text[:20] if text else ''}...")
        else:
            logger.bind(tag=TAG).info(f"ASR数据已加入上报队列: {conn.device_id}, 文件: {file_path}")
    except Exception as e:
        logger.bind(tag=TAG).error(f"加入ASR上报队列失败: {e}")
