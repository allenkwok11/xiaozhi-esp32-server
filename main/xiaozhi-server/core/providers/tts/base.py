import asyncio
from config.logger import setup_logging
import queue
import os
import json
import threading
from core.utils import p3
from core.handle.sendAudioHandle import sendAudioMessage
from core.handle.reportHandle import enqueue_tts_report
from abc import ABC, abstractmethod
from core.utils.tts import MarkdownCleaner
from core.utils.util import audio_to_data

TAG = __name__
logger = setup_logging()


class TTSProviderBase(ABC):
    def __init__(self, config, delete_audio_file):
        self.conn = None
        self.tts_timeout = 10
        self.delete_audio_file = delete_audio_file
        self.output_file = config.get("output_dir")
        self.tts_queue = queue.Queue()
        self.audio_play_queue = queue.Queue()

    @abstractmethod
    def generate_filename(self):
        pass

    def to_tts(self, text):
        tmp_file = self.generate_filename()
        try:
            max_repeat_time = 5
            text = MarkdownCleaner.clean_markdown(text)
            while not os.path.exists(tmp_file) and max_repeat_time > 0:
                try:
                    asyncio.run(self.text_to_speak(text, tmp_file))
                except Exception as e:
                    logger.bind(tag=TAG).warning(
                        f"语音生成失败{5 - max_repeat_time + 1}次: {text}，错误: {e}"
                    )
                    # 未执行成功，删除文件
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                    max_repeat_time -= 1

            if max_repeat_time > 0:
                logger.bind(tag=TAG).info(
                    f"语音生成成功: {text}:{tmp_file}，重试{5 - max_repeat_time}次"
                )
            else:
                logger.bind(tag=TAG).error(
                    f"语音生成失败: {text}，请检查网络或服务是否正常"
                )

            return tmp_file
        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to generate TTS file: {e}")
            return None

    @abstractmethod
    async def text_to_speak(self, text, output_file):
        pass

    def audio_to_pcm_data(self, audio_file_path):
        """音频文件转换为PCM编码"""
        return audio_to_data(audio_file_path, is_opus=False)

    def audio_to_opus_data(self, audio_file_path):
        """音频文件转换为Opus编码"""
        return audio_to_data(audio_file_path, is_opus=True)

    def startSession(self, conn):
        self.conn = conn
        self.tts_timeout = conn.config.get("tts_timeout", 10)
        # tts 消化线程
        self.tts_priority_thread = threading.Thread(
            target=self._tts_priority_thread, daemon=True
        )
        self.tts_priority_thread.start()

        # 音频播放 消化线程
        self.audio_play_priority_thread = threading.Thread(
            target=self._audio_play_priority_thread, daemon=True
        )
        self.audio_play_priority_thread.start()

    def _tts_priority_thread(self):
        while not self.conn.stop_event.is_set():
            text = None
            try:
                try:
                    item = self.tts_queue.get(timeout=1)
                    if item is None:
                        continue
                    future, text_index = item  # 解包获取 Future 和 text_index
                except queue.Empty:
                    if self.conn.stop_event.is_set():
                        break
                    continue
                if future is None:
                    continue
                text = None
                audio_datas, tts_file = [], None
                try:
                    logger.bind(tag=TAG).debug("正在处理TTS任务...")
                    tts_file, text, _ = future.result(timeout=self.tts_timeout)
                    if tts_file is None:
                        logger.bind(tag=TAG).error(
                            f"TTS出错： file is empty: {text_index}: {text}"
                        )
                    else:
                        logger.bind(tag=TAG).debug(f"TTS生成：文件路径: {tts_file}")
                        if os.path.exists(tts_file):
                            if tts_file.endswith(".p3"):
                                audio_datas, _ = p3.decode_opus_from_file(tts_file)
                            elif self.conn.audio_format == "pcm":
                                audio_datas, _ = self.audio_to_pcm_data(tts_file)
                            else:
                                audio_datas, _ = self.audio_to_opus_data(tts_file)
                            # 在这里上报TTS数据
                            enqueue_tts_report(
                                self.conn,
                                tts_file if text is None else text,
                                audio_datas,
                            )
                        else:
                            logger.bind(tag=TAG).error(f"TTS出错：文件不存在{tts_file}")
                except TimeoutError:
                    logger.bind(tag=TAG).error("TTS超时")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"TTS出错: {e}")
                if not self.conn.client_abort:
                    # 如果没有中途打断就发送语音
                    self.audio_play_queue.put((audio_datas, text, text_index))
                if (
                    self.delete_audio_file
                    and tts_file is not None
                    and os.path.exists(tts_file)
                    and tts_file.startswith(self.output_file)
                ):
                    os.remove(tts_file)
            except Exception as e:
                logger.bind(tag=TAG).error(f"TTS任务处理错误: {e}")
                self.conn.clearSpeakStatus()
                asyncio.run_coroutine_threadsafe(
                    self.conn.websocket.send(
                        json.dumps(
                            {
                                "type": "tts",
                                "state": "stop",
                                "session_id": self.session_id,
                            }
                        )
                    ),
                    self.conn.loop,
                )
                logger.bind(tag=TAG).error(f"tts_priority priority_thread: {text} {e}")

    def _audio_play_priority_thread(self):
        while not self.conn.stop_event.is_set():
            text = None
            try:
                try:
                    audio_datas, text, text_index = self.audio_play_queue.get(timeout=1)
                except queue.Empty:
                    if self.conn.stop_event.is_set():
                        break
                    continue
                future = asyncio.run_coroutine_threadsafe(
                    sendAudioMessage(self.conn, audio_datas, text, text_index),
                    self.conn.loop,
                )
                future.result()
            except Exception as e:
                logger.bind(tag=TAG).error(
                    f"audio_play_priority priority_thread: {text} {e}"
                )
