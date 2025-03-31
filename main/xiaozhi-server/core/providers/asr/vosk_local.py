import time
import wave
import os
import sys
import io
import json
from config.logger import setup_logging
from typing import Optional, Tuple, List
import uuid
import opuslib_next
from core.providers.asr.base import ASRProviderBase

from vosk import Model, KaldiRecognizer, SetLogLevel

TAG = __name__
logger = setup_logging()


# 捕获标准输出
class CaptureOutput:
    def __enter__(self):
        self._output = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._output

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self._original_stdout
        self.output = self._output.getvalue()
        self._output.close()

        # 将捕获到的内容通过 logger 输出
        if self.output:
            logger.bind(tag=TAG).info(self.output.strip())


class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        self.model_dir = config.get("model_dir")
        self.output_dir = config.get("output_dir")
        self.delete_audio_file = delete_audio_file
        self.sample_rate = 16000

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化VOSK模型
        with CaptureOutput():
            SetLogLevel(-1)
            logger.bind(tag=TAG).info(f"正在加载VOSK模型: {self.model_dir}")
            self.model = Model(self.model_dir)
            logger.bind(tag=TAG).info("VOSK模型加载完成")

    def save_audio_to_file(self, opus_data: List[bytes], session_id: str) -> str:
        """将Opus音频数据解码并保存为WAV文件"""
        file_name = f"asr_{session_id}_{uuid.uuid4()}.wav"
        file_path = os.path.join(self.output_dir, file_name)

        decoder = opuslib_next.Decoder(self.sample_rate, 1)  # 16kHz, 单声道
        pcm_data = []

        for opus_packet in opus_data:
            try:
                pcm_frame = decoder.decode(opus_packet, 960)  # 960 samples = 60ms
                pcm_data.append(pcm_frame)
            except opuslib_next.OpusError as e:
                logger.bind(tag=TAG).error(f"Opus解码错误: {e}", exc_info=True)

        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes = 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(b"".join(pcm_data))

        return file_path

    async def speech_to_text(self, opus_data: List[bytes], session_id: str) -> Tuple[Optional[str], Optional[str]]:
        """语音转文本主处理逻辑"""
        file_path = None
        try:
            # 保存音频文件
            start_time = time.time()
            file_path = self.save_audio_to_file(opus_data, session_id)
            logger.bind(tag=TAG).debug(f"音频文件保存耗时: {time.time() - start_time:.3f}s | 路径: {file_path}")

            # 语音识别
            start_time = time.time()
            
            # 创建识别器
            recognizer = KaldiRecognizer(self.model, self.sample_rate)
            recognizer.SetWords(True)  # 启用词级时间戳
            
            # 读取WAV文件并进行识别
            with wave.open(file_path, "rb") as wf:
                # 确保音频格式正确
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.sample_rate:
                    logger.bind(tag=TAG).error(f"音频格式不支持: 需要16kHz, 16-bit, 单声道")
                    return "", file_path
                
                # 分块处理音频数据
                result_text = ""
                while True:
                    data = wf.readframes(4000)  # 读取音频块
                    if len(data) == 0:
                        break
                    
                    if recognizer.AcceptWaveform(data):
                        result_json = json.loads(recognizer.Result())
                        if "text" in result_json and result_json["text"].strip():
                            result_text += result_json["text"] + " "
                
                # 获取最终结果
                final_result = json.loads(recognizer.FinalResult())
                if "text" in final_result and final_result["text"].strip():
                    result_text += final_result["text"]
                
                result_text = result_text.strip()
                
            logger.bind(tag=TAG).debug(f"语音识别耗时: {time.time() - start_time:.3f}s | 结果: {result_text}")

            return result_text, file_path

        except Exception as e:
            logger.bind(tag=TAG).error(f"语音识别失败: {e}", exc_info=True)
            return "", None

        finally:
            # 文件清理逻辑
            if self.delete_audio_file and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.bind(tag=TAG).debug(f"已删除临时音频文件: {file_path}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"文件删除失败: {file_path} | 错误: {e}")