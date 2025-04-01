import asyncio
import gc
import io
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

import torch
import torchaudio

from config.logger import setup_logging
import os
import numpy as np
import opuslib_next
from pydub import AudioSegment
from abc import ABC, abstractmethod
from core.utils import textUtils
import queue

from core.providers.tts.dto.dto import MsgType, TTSMessageDTO, SentenceType

TAG = __name__
logger = setup_logging()


class TTSProviderBase(ABC):
    def __init__(self, config, delete_audio_file):
        self.config = config
        self.delete_audio_file = delete_audio_file
        self.output_file = config.get("output_dir")
        self.tts_text_queue = queue.Queue()
        self.tts_audio_queue = queue.Queue()
        self.enable_two_way = False
        self.stop_event = threading.Event()

        self.tts_text_buff = []
        self.punctuations = (
            "。",
            "？",
            "！",
            "；",
            "：",
            ".",
            "?",
            "!",
            ";",
            ":",
            " ",
            ",",
            "，",
        )
        self.tts_request = False
        self.processed_chars = 0
        self.stream = False
        self.last_to_opus_raw = b""

        # 启动tts_text_queue监听线程
        # 线程任务相关
        self.loop = asyncio.get_event_loop()
        self.process_tasks_loop = asyncio.get_event_loop()
        self.max_workers = self.config.get("TTS_SET", {}).get("MAX_WORKERS", 3)
        self.active_tasks = set()  # 追踪当前运行的任务
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    async def open_audio_channels(self):
        # 启动tts_text_queue监听线程
        tts_priority = threading.Thread(
            target=self._tts_text_priority_thread, daemon=True
        )
        tts_priority.start()

    async def stop_listen_resource(self):
        """资源清理方法"""
        self.stop_event.set()
        self.tts_text_queue = None
        self.tts_audio_queue = None
        gc.collect()  # 强制执行垃圾回收

    async def close(self):
        pass

    def _get_segment_text(self):
        # 合并当前全部文本并处理未分割部分
        full_text = "".join(self.tts_text_buff)
        current_text = full_text[self.processed_chars :]  # 从未处理的位置开始
        last_punct_pos = -1
        for punct in self.punctuations:
            pos = current_text.rfind(punct)
            if (pos != -1 and last_punct_pos == -1) or (
                pos != -1 and pos < last_punct_pos
            ):
                last_punct_pos = pos
        if last_punct_pos != -1:
            segment_text_raw = current_text[: last_punct_pos + 1]
            segment_text = textUtils.get_string_no_punctuation_or_emoji(
                segment_text_raw
            )
            self.processed_chars += len(segment_text_raw)  # 更新已处理字符位置
            return segment_text
        else:
            return None

    async def process_generator(self, generator):
        async for tts_data in generator:
            self.tts_audio_queue.put(tts_data)

    def _tts_text_priority_thread(self):
        logger.bind(tag=TAG).info("开始监听tts文本")
        if self.enable_two_way:
            self._enable_two_way_tts()
        else:
            self._no_enable_two_way_tts()

    async def start_session(self, session_id):
        pass

    async def finish_session(self, session_id):
        pass

    async def tts_one_sentence(self, text):
        uuid_str = str(uuid.uuid4()).replace("-", "")
        self.tts.tts_text_queue.put(
            TTSMessageDTO(u_id=uuid_str, msg_type=MsgType.START_TTS_REQUEST, content="")
        )
        self.tts.tts_text_queue.put(
            TTSMessageDTO(
                u_id=uuid_str, msg_type=MsgType.TTS_TEXT_REQUEST, content=text
            )
        )
        self.tts.tts_text_queue.put(
            TTSMessageDTO(
                u_id=uuid_str, msg_type=MsgType.STOP_TTS_REQUEST, content=text
            )
        )

    def _enable_two_way_tts(self):
        while not self.stop_event.is_set():
            try:
                ttsMessageDTO = self.tts_text_queue.get()
                msg_type = ttsMessageDTO.msg_type
                if msg_type == MsgType.START_TTS_REQUEST:
                    # 开始传输tts文本
                    self.tts_request = True
                    self.u_id = ttsMessageDTO.u_id
                    # 开启session
                    future = asyncio.run_coroutine_threadsafe(
                        self.start_session(ttsMessageDTO.u_id), loop=self.loop
                    )
                    future.result()
                    # await self.start_session(ttsMessageDTO.u_id)
                elif self.tts_request and msg_type == MsgType.TTS_TEXT_REQUEST:
                    future = asyncio.run_coroutine_threadsafe(
                        self.text_to_speak(
                            u_id=ttsMessageDTO.u_id, text=ttsMessageDTO.content
                        ),
                        loop=self.loop,
                    )
                    future.result()
                elif msg_type == MsgType.STOP_TTS_REQUEST:
                    self.tts_request = False
                    future = asyncio.run_coroutine_threadsafe(
                        self.finish_session(ttsMessageDTO.u_id), loop=self.loop
                    )
                    future.result()

            except Exception as e:
                logger.bind(tag=TAG).error(f"Failed to process TTS text: {e}")
                # 报错了。要关闭说话
                self.tts_audio_queue.put(
                    TTSMessageDTO(
                        u_id=self.u_id,
                        msg_type=MsgType.STOP_TTS_RESPONSE,
                        content=[],
                        tts_finish_text="",
                        sentence_type=None,
                    )
                )
                traceback.print_exc()

    def _no_enable_two_way_tts(self):
        # 为这个线程创建一个新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while not self.stop_event.is_set():
            try:
                ttsMessageDTO = self.tts_text_queue.get()
                msg_type = ttsMessageDTO.msg_type
                if not self.enable_two_way:
                    if msg_type == MsgType.START_TTS_REQUEST:
                        # 开始传输tts文本
                        self.tts_request = True
                        self.processed_chars = 0
                        self.tts_text_buff = []
                    elif self.tts_request and msg_type == MsgType.TTS_TEXT_REQUEST:
                        self.tts_text_buff.append(ttsMessageDTO.content)
                    elif msg_type == MsgType.STOP_TTS_REQUEST:
                        # 结束传输tts文本,处理最尾巴的数据
                        self.tts_request = False
                        segment_text = self._get_segment_text()
                        if segment_text:
                            # 修改部分：创建协程对象
                            # 修改部分：创建协程对象
                            tts_generator = self.text_to_speak(
                                ttsMessageDTO.u_id,
                                segment_text,
                                True if msg_type == MsgType.STOP_TTS_REQUEST else False,
                                (
                                    True
                                    if msg_type == MsgType.START_TTS_REQUEST
                                    else False
                                ),
                            )
                            future = asyncio.run_coroutine_threadsafe(
                                self.process_generator(tts_generator), self.loop
                            )
                            self.active_tasks.add(future)
                        if self.active_tasks:

                            async def wrap_future(future):
                                return await asyncio.wrap_future(future)

                            wrapped_tasks = [
                                wrap_future(task) for task in self.active_tasks
                            ]
                            done, _ = loop.run_until_complete(
                                asyncio.wait(wrapped_tasks)
                            )
                            self.active_tasks -= done

                        # 发送合成结束
                        self.tts_audio_queue.put(
                            TTSMessageDTO(
                                u_id=ttsMessageDTO.u_id,
                                msg_type=MsgType.STOP_TTS_RESPONSE,
                                content=[],
                                tts_finish_text="",
                                sentence_type=SentenceType.SENTENCE_END,
                            )
                        )

                    segment_text = self._get_segment_text()
                    if segment_text:
                        # 确保这里得到的是协程对象
                        tts_generator = self.text_to_speak(
                            ttsMessageDTO.u_id,
                            segment_text,
                            msg_type == MsgType.STOP_TTS_REQUEST,
                            msg_type == MsgType.START_TTS_REQUEST,
                        )
                        # 提交协程到事件循环
                        tts_generator_future = asyncio.run_coroutine_threadsafe(
                            self.process_generator(tts_generator), loop
                        )
                        self.active_tasks.add(tts_generator_future)
                        if len(self.active_tasks) >= self.max_workers:
                            # 等待所有任务完成
                            try:

                                async def wrap_future(future):
                                    return await asyncio.wrap_future(future)

                                wrapped_tasks = [
                                    wrap_future(task) for task in self.active_tasks
                                ]
                                done, _ = loop.run_until_complete(
                                    asyncio.wait(wrapped_tasks)
                                )
                                self.active_tasks -= done
                            except Exception as e:
                                logger.bind(tag=TAG).error(
                                    f"Failed to process TTS text: {e}"
                                )
                                traceback.print_exc()
                else:
                    pass
            except Exception as e:
                logger.bind(tag=TAG).error(f"Failed to process TTS text: {e}")
                traceback.print_exc()

    @abstractmethod
    def generate_filename(self):
        pass

    def to_tts(self, text):
        tmp_file = self.generate_filename()
        try:
            max_repeat_time = 5
            while not os.path.exists(tmp_file) and max_repeat_time > 0:
                asyncio.run(self.text_to_speak(text, tmp_file))
                if not os.path.exists(tmp_file):
                    max_repeat_time = max_repeat_time - 1
                    logger.bind(tag=TAG).error(
                        f"语音生成失败: {text}:{tmp_file}，再试{max_repeat_time}次"
                    )

            if max_repeat_time > 0:
                logger.bind(tag=TAG).info(
                    f"语音生成成功: {text}:{tmp_file}，重试{5 - max_repeat_time}次"
                )

            return tmp_file
        except Exception as e:
            logger.bind(tag=TAG).info(f"Failed to generate TTS file: {e}")
            return None

    def to_tts_stream(self, u_id, text, queue: queue.Queue, text_index=0):
        try:
            asyncio.run(self.text_to_speak_stream(text, queue, text_index))
        except Exception as e:
            logger.bind(tag=TAG).info(f"Failed to generate TTS file: {e}")
            return None

    @abstractmethod
    async def text_to_speak(self, u_id, text, is_last_text=False, is_first_text=False):
        pass

    async def text_to_speak_stream(self, text, queue: queue.Queue, text_index=0):
        raise Exception("该TTS还没有实现stream模式")

    def audio_to_opus_data(self, audio_file_path):
        """音频文件转换为Opus编码"""
        # 获取文件后缀名
        file_type = os.path.splitext(audio_file_path)[1]
        if file_type:
            file_type = file_type.lstrip(".")
        audio = AudioSegment.from_file(audio_file_path, format=file_type)

        # 转换为单声道/16kHz采样率/16位小端编码（确保与编码器匹配）
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)

        # 音频时长(秒)
        duration = len(audio) / 1000.0

        # 获取原始PCM数据（16位小端）
        raw_data = audio.raw_data

        # 初始化Opus编码器
        encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)

        # 编码参数
        frame_duration = 60  # 60ms per frame
        frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

        opus_datas = []
        # 按帧处理所有音频数据（包括最后一帧可能补零）
        for i in range(0, len(raw_data), frame_size * 2):  # 16bit=2bytes/sample
            # 获取当前帧的二进制数据
            chunk = raw_data[i : i + frame_size * 2]

            # 如果最后一帧不足，补零
            if len(chunk) < frame_size * 2:
                chunk += b"\x00" * (frame_size * 2 - len(chunk))

            # 转换为numpy数组处理
            np_frame = np.frombuffer(chunk, dtype=np.int16)

            # 编码Opus数据
            opus_data = encoder.encode(np_frame.tobytes(), frame_size)
            opus_datas.append(opus_data)

        return opus_datas, duration

    def get_audio_from_tts(self, data_bytes, src_rate, to_rate=16000):
        tts_speech = torch.from_numpy(
            np.array(np.frombuffer(data_bytes, dtype=np.int16))
        ).unsqueeze(dim=0)
        with io.BytesIO() as bf:
            torchaudio.save(bf, tts_speech, src_rate, format="wav")
            audio = AudioSegment.from_file(bf, format="wav")
        audio = audio.set_channels(1).set_frame_rate(to_rate)
        return audio

    def wav_to_opus_data_audio_raw(self, raw_data_var, is_end=False):
        raw_data = self.last_to_opus_raw + raw_data_var
        self.last_to_opus_raw = b""
        # 初始化Opus编码器
        encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)

        # 编码参数
        frame_duration = 60  # 60ms per frame
        frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

        opus_datas = []
        # 按帧处理所有音频数据（包括最后一帧可能补零）
        for i in range(0, len(raw_data), frame_size * 2):  # 16bit=2bytes/sample
            # 获取当前帧的二进制数据
            chunk = raw_data[i : i + frame_size * 2]

            # 如果最后一帧不足，补零
            # 缓存记录一下
            if len(chunk) < frame_size * 2 and not is_end:
                logger.bind(tag=TAG).info("如果最后一帧不足,缓存记录一下")
                self.last_to_opus_raw = chunk
                break
            if len(chunk) < frame_size * 2 and is_end:
                logger.bind(tag=TAG).info("是最后一句了，补零")
                chunk += b"\x00" * (frame_size * 2 - len(chunk))

            # 转换为numpy数组处理
            np_frame = np.frombuffer(chunk, dtype=np.int16)

            # 编码Opus数据
            opus_data = encoder.encode(np_frame.tobytes(), frame_size)
            opus_datas.append(opus_data)

        return opus_datas
