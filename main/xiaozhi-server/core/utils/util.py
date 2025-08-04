import json
import socket
import subprocess
import re
import os
import wave
from io import BytesIO
from core.utils import p3
import numpy as np
import requests
import opuslib_next
from pydub import AudioSegment
import copy
from loguru import logger
import math
import time
from typing import Dict, Optional

TAG = __name__

# Global emotion persistence tracker
class EmotionPersistenceTracker:
    def __init__(self):
        self.persistent_emotions = {}  # {emotion: {'score': float, 'timestamp': float, 'chunk_count': int}}
        self.chunk_counter = 0
        
    def add_llm_emotion(self, emotion: str, base_score: float = 5.0):
        """Add or update LLM-detected emotion with fresh score"""
        current_time = time.time()
        self.persistent_emotions[emotion] = {
            'score': base_score,
            'timestamp': current_time,
            'chunk_count': self.chunk_counter,
            'source': 'llm'
        }
        logger.info(f"🎭 LLM emotion '{emotion}' added with score {base_score} at chunk {self.chunk_counter}")
    
    def decay_emotions(self, half_life_chunks: float = 3.0, minimum_score: float = 0.1):
        """Apply radioactive decay to persistent emotions"""
        self.chunk_counter += 1
        expired_emotions = []
        
        for emotion, data in self.persistent_emotions.items():
            chunks_elapsed = self.chunk_counter - data['chunk_count']
            
            # Radioactive decay formula: N(t) = N₀ * (1/2)^(t/t_half)
            decay_factor = (0.5) ** (chunks_elapsed / half_life_chunks)
            new_score = data['score'] * decay_factor
            
            if new_score >= minimum_score:
                data['score'] = new_score
                logger.debug(f"🔄 Emotion '{emotion}' decayed: {data['score']:.2f} -> {new_score:.2f} (chunks: {chunks_elapsed})")
            else:
                expired_emotions.append(emotion)
                logger.info(f"💀 Emotion '{emotion}' expired after {chunks_elapsed} chunks (score: {new_score:.3f} < {minimum_score})")
        
        # Remove expired emotions
        for emotion in expired_emotions:
            del self.persistent_emotions[emotion]
    
    def get_persistent_scores(self) -> Dict[str, float]:
        """Get current scores of all persistent emotions"""
        return {emotion: data['score'] for emotion, data in self.persistent_emotions.items()}
    
    def clear(self):
        """Clear all persistent emotions (for testing or reset)"""
        self.persistent_emotions.clear()
        self.chunk_counter = 0
        logger.info("🧹 Emotion persistence tracker cleared")

# Global instance
emotion_persistence = EmotionPersistenceTracker()

# Import emotion manager - avoid circular import by importing here
try:
    from core.utils.emotion_manager import emotion_manager
except ImportError:
    # Fallback if emotion_manager is not available
    emotion_manager = None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to Google's DNS servers
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return "127.0.0.1"


def is_private_ip(ip_addr):
    """
    Check if an IP address is a private IP address (compatible with IPv4 and IPv6).

    @param {string} ip_addr - The IP address to check.
    @return {bool} True if the IP address is private, False otherwise.
    """
    try:
        # Validate IPv4 or IPv6 address format
        if not re.match(
            r"^(\d{1,3}\.){3}\d{1,3}$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$", ip_addr
        ):
            return False  # Invalid IP address format

        # IPv4 private address ranges
        if "." in ip_addr:  # IPv4 address
            ip_parts = list(map(int, ip_addr.split(".")))
            if ip_parts[0] == 10:
                return True  # 10.0.0.0/8 range
            elif ip_parts[0] == 172 and 16 <= ip_parts[1] <= 31:
                return True  # 172.16.0.0/12 range
            elif ip_parts[0] == 192 and ip_parts[1] == 168:
                return True  # 192.168.0.0/16 range
            elif ip_addr == "127.0.0.1":
                return True  # Loopback address
            elif ip_parts[0] == 169 and ip_parts[1] == 254:
                return True  # Link-local address 169.254.0.0/16
            else:
                return False  # Not a private IPv4 address
        else:  # IPv6 address
            ip_addr = ip_addr.lower()
            if ip_addr.startswith("fc00:") or ip_addr.startswith("fd00:"):
                return True  # Unique Local Addresses (FC00::/7)
            elif ip_addr == "::1":
                return True  # Loopback address
            elif ip_addr.startswith("fe80:"):
                return True  # Link-local unicast addresses (FE80::/10)
            else:
                return False  # Not a private IPv6 address

    except (ValueError, IndexError):
        return False  # IP address format error or insufficient segments


def get_ip_info(ip_addr, logger):
    try:
        if is_private_ip(ip_addr):
            ip_addr = ""
        url = f"https://whois.pconline.com.cn/ipJson.jsp?json=true&ip={ip_addr}"
        resp = requests.get(url).json()
        ip_info = {"city": resp.get("city")}
        return ip_info
    except Exception as e:
        logger.bind(tag=TAG).error(f"Error getting client ip info: {e}")
        return {}


def write_json_file(file_path, data):
    """将数据写入 JSON 文件"""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def is_punctuation_or_emoji(char):
    """检查字符是否为空格、指定标点或表情符号"""
    # 定义需要去除的中英文标点（包括全角/半角）
    punctuation_set = {
        "，",
        ",",  # 中文逗号 + 英文逗号
        "-",
        "－",  # 英文连字符 + 中文全角横线
        "、",  # 中文顿号
        "“",
        "”",
        '"',  # 中文双引号 + 英文引号
        "：",
        ":",  # 中文冒号 + 英文冒号
    }
    if char.isspace() or char in punctuation_set:
        return True
    # 检查表情符号（保留原有逻辑）
    code_point = ord(char)
    emoji_ranges = [
        (0x1F600, 0x1F64F),
        (0x1F300, 0x1F5FF),
        (0x1F680, 0x1F6FF),
        (0x1F900, 0x1F9FF),
        (0x1FA70, 0x1FAFF),
        (0x2600, 0x26FF),
        (0x2700, 0x27BF),
    ]
    return any(start <= code_point <= end for start, end in emoji_ranges)


def get_string_no_punctuation_or_emoji(s):
    """去除字符串首尾的空格、标点符号和表情符号"""
    chars = list(s)
    # 处理开头的字符
    start = 0
    while start < len(chars) and is_punctuation_or_emoji(chars[start]):
        start += 1
    # 处理结尾的字符
    end = len(chars) - 1
    while end >= start and is_punctuation_or_emoji(chars[end]):
        end -= 1
    return "".join(chars[start : end + 1])


def remove_punctuation_and_length(text):
    # 全角符号和半角符号的Unicode范围
    full_width_punctuations = (
        "！＂＃＄％＆＇（）＊＋，－。／：；＜＝＞？＠［＼］＾＿｀｛｜｝～"
    )
    half_width_punctuations = r'!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
    space = " "  # 半角空格
    full_width_space = "　"  # 全角空格

    # 去除全角和半角符号以及空格
    result = "".join(
        [
            char
            for char in text
            if char not in full_width_punctuations
            and char not in half_width_punctuations
            and char not in space
            and char not in full_width_space
        ]
    )

    if result == "Yeah":
        return 0, ""
    return len(result), result


def check_model_key(modelType, modelKey):
    if "你" in modelKey:
        return f"config error: AKI key of {modelType} not configured, current value is: {modelKey}"
    return None


def parse_string_to_list(value, separator=";"):
    """
    将输入值转换为列表
    Args:
        value: 输入值，可以是 None、字符串或列表
        separator: 分隔符，默认为分号
    Returns:
        list: 处理后的列表
    """
    if value is None or value == "":
        return []
    elif isinstance(value, str):
        return [item.strip() for item in value.split(separator) if item.strip()]
    elif isinstance(value, list):
        return value
    return []


def check_ffmpeg_installed():
    ffmpeg_installed = False
    try:
        # 执行ffmpeg -version命令，并捕获输出
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,  # 如果返回码非零则抛出异常
        )
        # 检查输出中是否包含版本信息（可选）
        output = result.stdout + result.stderr
        if "ffmpeg version" in output.lower():
            ffmpeg_installed = True
        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 命令执行失败或未找到
        ffmpeg_installed = False
    if not ffmpeg_installed:
        error_msg = "FFmpeg is not properly installed on your computer.\n"
        error_msg += "\nRecommended actions:\n"
        error_msg += "1. Follow the project installation guide to correctly activate your conda environment.\n"
        error_msg += "2. Refer to the installation guide for instructions on how to install FFmpeg within the conda environment.\n"
        raise ValueError(error_msg)


def extract_json_from_string(input_string):
    """提取字符串中的 JSON 部分"""
    pattern = r"(\{.*\})"
    match = re.search(pattern, input_string, re.DOTALL)  # 添加 re.DOTALL
    if match:
        return match.group(1)  # 返回提取的 JSON 字符串
    return None


def analyze_emotion(text):
    """
    分析文本情感并返回对应的emoji名称（支持中英文）
    Now uses emotion_manager for configuration
    """
    if not text or not isinstance(text, str):
        default_emotion = emotion_manager.default_emotion if emotion_manager else "neutral"
        logger.info(f"📝 Text is empty or invalid, returning default emotion: '{default_emotion}'")
        return default_emotion

    original_text = text
    text = text.lower().strip()

    # Check if emotion_manager is available
    if not emotion_manager:
        logger.warning("⚠️ emotion_manager not available, returning neutral")
        return "neutral"

    logger.info(f"🔍 Starting emotion analysis for text: '{original_text[:100]}...'")

    # 检查是否包含现有emoji
    for emotion in emotion_manager.get_emotion_list():
        emoji = emotion_manager.get_emoji(emotion)
        if emoji in original_text:
            logger.info(f"😀 Detected emoji {emoji}, returning emotion: '{emotion}'")
            return emotion

    # 标点符号分析
    has_exclamation = "!" in original_text or "！" in original_text
    has_question = "?" in original_text or "？" in original_text
    has_ellipsis = "..." in original_text or "…" in original_text

    # 特殊句型判断（中英文）
    # 赞美他人 - 圣诞节主题
    if any(
        phrase in text
        for phrase in [
            "你真",
            "你好",
            "您真",
            "你真棒",
            "你好厉害",
            "你太强了",
            "你真好",
            "你真聪明",
            "you are",
            "you're",
            "you look",
            "you seem",
            "so smart",
            "so kind",
        ]
    ):
        logger.info("💖 Detected praise pattern, returning emotion: 'heart'")
        return "heart"
    # 自我赞美 - 圣诞节主题
    if any(
        phrase in text
        for phrase in [
            "我真",
            "我最",
            "我太棒了",
            "我厉害",
            "我聪明",
            "我优秀",
            "i am",
            "i'm",
            "i feel",
            "so good",
            "so happy",
        ]
    ):
        logger.info("🧝 Detected self-praise pattern, returning emotion: 'elf'")
        return "elf"
    # 晚安/睡觉相关 - 保持一致
    if any(
        phrase in text
        for phrase in [
            "睡觉",
            "晚安",
            "睡了",
            "好梦",
            "休息了",
            "去睡了",
            "sleep",
            "good night",
            "bedtime",
            "go to bed",
        ]
    ):
        logger.info("😴 Detected sleep-related pattern, returning emotion: 'sleep'")
        return "sleep"
    # 疑问句 - 圣诞节主题
    if has_question and not has_exclamation:
        logger.info("❓ Detected question pattern, returning emotion: 'star'")
        return "star"
    # 强烈情感（感叹号）- 圣诞节主题
    if has_exclamation and not has_question:
        # 对于感叹句，默认使用铃铛
        logger.info("❗ Detected exclamation pattern, returning emotion: 'bell'")
        return "bell"
    # 省略号（表示犹豫或思考）- 圣诞节主题
    if has_ellipsis:
        logger.info("❄️ Detected ellipsis pattern, returning emotion: 'snowman'")
        return "snowman"

    # 关键词匹配（带权重）
    logger.info("🔍 Starting keyword matching analysis...")
    emotion_scores = {emotion: 0 for emotion in emotion_manager.get_emotion_list()}

    # Use emotion_manager to get keywords for each emotion
    matched_keywords = []
    for emotion in emotion_manager.get_emotion_list():
        keywords = emotion_manager.get_keywords_for_emotion(emotion)
        for keyword in keywords:
            if keyword in text:
                emotion_scores[emotion] += 1
                matched_keywords.append(f"{keyword}({emotion})")

    if matched_keywords:
        logger.info(f"✅ Matched keywords: {', '.join(matched_keywords[:5])}{'...' if len(matched_keywords) > 5 else ''}")
    else:
        logger.info("❌ No keywords matched")

    # 给长文本中的重复关键词额外加分
    if len(text) > 20:  # 长文本
        logger.info("📏 Long text detected, calculating repeated keyword weights...")
        for emotion in emotion_manager.get_emotion_list():
            keywords = emotion_manager.get_keywords_for_emotion(emotion)
            for keyword in keywords:
                repeat_count = text.count(keyword)
                if repeat_count > 1:
                    bonus_score = int(repeat_count * 0.5)
                    emotion_scores[emotion] += bonus_score
                    logger.debug(f"🔄 Keyword '{keyword}' repeated {repeat_count} times, {emotion} +{bonus_score} points")

    # Apply weighted scoring system instead of simple priority
    emotion_weights = emotion_manager.get_all_emotion_weights()
    weighted_scores = {}
    
    for emotion, raw_score in emotion_scores.items():
        if raw_score > 0:
            weight = emotion_weights.get(emotion, 1.0)
            weighted_score = raw_score * weight
            weighted_scores[emotion] = weighted_score
            logger.debug(f"🎯 {emotion}: raw_score={raw_score} × weight={weight} = weighted_score={weighted_score:.2f}")
    
    # Log emotion scores (both raw and weighted)
    if weighted_scores:
        sorted_weighted = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_raw = sorted([(e, emotion_scores[e]) for e in weighted_scores.keys()], key=lambda x: x[1], reverse=True)
        logger.info(f"� Raw scores: {sorted_raw}")
        logger.info(f"⚖️ Weighted scores: {[(e, f'{s:.2f}') for e, s in sorted_weighted]}")
    
    if not weighted_scores:
        default_emotion = emotion_manager.default_emotion
        logger.info(f"🤔 No matching emotions found, returning default emotion: '{default_emotion}'")
        return default_emotion

    # Select emotion with highest weighted score
    best_emotion = max(weighted_scores.items(), key=lambda x: x[1])
    selected_emotion = best_emotion[0]
    final_score = best_emotion[1]
    
    logger.info(f"� Selected emotion: '{selected_emotion}' (weighted score: {final_score:.2f})")
    return selected_emotion


def parse_llm_response_with_emotion(text):
    """
    Parse LLM response to separate emotion and clean text
    Handles formats like [emotion:description] or [EMOTION:emotion_name]
    Returns tuple: (clean_text, emotion)
    """
    if not text:
        return text, None
    
    logger.info(f"🔍 Parsing text for emotion tags: '{text}'")
    
    # Look for [emotion:description] or [EMOTION:emotion_name] pattern
    import re
    
    # Pattern to match [EMOTION:emotion_name] - capture what comes after the colon, handle backticks
    emotion_pattern = r'^\[EMOTION:`?([^`\]]+)`?\]\s*'
    match = re.match(emotion_pattern, text.strip())
    
    if match:
        emotion = match.group(1).lower().strip()
        # Remove the emotion tag from the text
        clean_text = re.sub(emotion_pattern, '', text.strip())
        
        logger.info(f"🎭 Found EMOTION tag: '{match.group(0)}' -> emotion: '{emotion}', clean_text: '{clean_text}'")
        
        # Validate that the emotion exists in our configuration
        if emotion_manager and emotion in emotion_manager.get_emotion_list():
            logger.info(f"🎭 Parsed LLM emotion '{emotion}' from EMOTION tag")
            
            # Store LLM emotion for persistence if enabled
            if emotion_manager.is_persistence_enabled():
                persistence_config = emotion_manager.get_persistence_config()
                base_score = persistence_config.get('llm_base_score', 5.0)
                emotion_persistence.add_llm_emotion(emotion, base_score)
            
            return clean_text, emotion
        else:
            logger.warning(f"⚠️ LLM provided unknown emotion '{emotion}', ignoring tag")
            return clean_text, None
    
    # Also check for [emotion:description] format (like [sleep:sleep] or [cookie:愉悦])
    emotion_pattern_alt = r'^\[([^:]+):[^]]+\]\s*'
    match = re.match(emotion_pattern_alt, text.strip())
    
    if match:
        emotion = match.group(1).lower().strip()
        # Remove the emotion tag from the text
        clean_text = re.sub(emotion_pattern_alt, '', text.strip())
        
        logger.info(f"🎭 Found alt emotion tag: '{match.group(0)}' -> emotion: '{emotion}', clean_text: '{clean_text}'")
        
        # Validate that the emotion exists in our configuration
        if emotion_manager and emotion in emotion_manager.get_emotion_list():
            logger.info(f"🎭 Parsed LLM emotion '{emotion}' from alt tag")
            
            # Store LLM emotion for persistence if enabled
            if emotion_manager.is_persistence_enabled():
                persistence_config = emotion_manager.get_persistence_config()
                base_score = persistence_config.get('llm_base_score', 5.0)
                emotion_persistence.add_llm_emotion(emotion, base_score)
            
            return clean_text, emotion
        else:
            logger.warning(f"⚠️ LLM provided unknown emotion '{emotion}', ignoring tag")
            return clean_text, None
    
    logger.info(f"🤔 No emotion tag found in text")
    return text, None


def select_emotion_with_persistence(text: str, llm_emotion: Optional[str] = None, persistence_tracker: Optional[EmotionPersistenceTracker] = None) -> str:
    """
    Unified emotion selection with persistence and decay
    Combines LLM emotions (fresh + persistent) with keyword analysis
    Returns the best emotion based on comparable scoring
    """
    if not emotion_manager:
        logger.warning("⚠️ emotion_manager not available")
        return "neutral"
    
    # Use global persistence tracker if none provided
    if persistence_tracker is None:
        persistence_tracker = emotion_persistence
    
    persistence_config = emotion_manager.get_persistence_config()
    is_persistence_enabled = emotion_manager.is_persistence_enabled()
    
    logger.info(f"🎭 Starting unified emotion selection for: '{text[:50]}...'")
    
    # Step 1: Decay existing persistent emotions
    if is_persistence_enabled:
        half_life = persistence_config.get('half_life_chunks', 3.0)
        min_score = persistence_config.get('minimum_score', 0.1)
        persistence_tracker.decay_emotions(half_life, min_score)
    
    # Step 2: Get all emotion scores
    emotion_scores = {}
    
    # A) Fresh LLM emotion (highest priority if provided)
    if llm_emotion and llm_emotion in emotion_manager.get_emotion_list():
        base_score = persistence_config.get('llm_base_score', 5.0)
        llm_multiplier = persistence_config.get('llm_multiplier', 1.0)
        emotion_scores[llm_emotion] = base_score * llm_multiplier
        logger.info(f"✨ Fresh LLM emotion '{llm_emotion}': score = {emotion_scores[llm_emotion]:.2f}")
        
        # Add fresh LLM emotion to persistence tracker
        if is_persistence_enabled:
            persistence_tracker.add_llm_emotion(llm_emotion, base_score)
    
    # B) Persistent LLM emotions (decayed scores)
    if is_persistence_enabled:
        persistent_scores = persistence_tracker.get_persistent_scores()
        llm_multiplier = persistence_config.get('llm_multiplier', 1.0)
        for emotion, score in persistent_scores.items():
            # Fresh LLM emotion takes precedence over persistent one
            if emotion not in emotion_scores:
                emotion_scores[emotion] = score * llm_multiplier
                logger.info(f"🔄 Persistent LLM emotion '{emotion}': score = {emotion_scores[emotion]:.2f}")
    
    # C) Keyword-based emotions (using existing analyze_emotion logic)
    keyword_scores = _calculate_keyword_scores(text)
    keyword_multiplier = persistence_config.get('keyword_multiplier', 1.0)
    
    for emotion, score in keyword_scores.items():
        # Only add keyword score if no LLM score exists, or combine them intelligently
        if emotion not in emotion_scores:
            emotion_scores[emotion] = score * keyword_multiplier
            logger.info(f"🔤 Keyword emotion '{emotion}': score = {emotion_scores[emotion]:.2f}")
        else:
            # Optional: Add keyword reinforcement to existing LLM emotions
            reinforcement = score * keyword_multiplier * 0.2  # 20% reinforcement
            emotion_scores[emotion] += reinforcement
            logger.debug(f"💪 Keyword reinforcement for '{emotion}': +{reinforcement:.2f}")
    
    # Step 3: Select best emotion
    if not emotion_scores:
        default_emotion = emotion_manager.default_emotion
        logger.info(f"🤔 No emotions detected, using default: '{default_emotion}'")
        return default_emotion
    
    # Find highest scoring emotion
    best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
    selected_emotion = best_emotion[0]
    final_score = best_emotion[1]
    
    # Log final results
    sorted_scores = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
    logger.info(f"🏆 Final emotion scores: {[(e, f'{s:.2f}') for e, s in sorted_scores[:3]]}")
    logger.info(f"🎯 Selected emotion: '{selected_emotion}' (final score: {final_score:.2f})")
    
    return selected_emotion


def _calculate_keyword_scores(text: str) -> Dict[str, float]:
    """
    Calculate keyword-based emotion scores (extracted from analyze_emotion)
    Returns raw scores before weight multiplication
    """
    if not text or not emotion_manager:
        return {}
    
    text_lower = text.lower().strip()
    emotion_scores = {}
    
    # Initialize scores for all emotions
    for emotion in emotion_manager.get_emotion_list():
        emotion_scores[emotion] = 0
    
    # Score based on keyword matches
    matched_keywords = []
    for emotion in emotion_manager.get_emotion_list():
        keywords = emotion_manager.get_keywords_for_emotion(emotion)
        emotion_weight = emotion_manager.get_emotion_weight(emotion)
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Base score for keyword match, then apply emotion weight
                base_match_score = 1.0
                weighted_score = base_match_score * emotion_weight
                emotion_scores[emotion] += weighted_score
                matched_keywords.append(f"{keyword}({emotion})")
    
    # Bonus for repeated keywords in long text
    if len(text) > 20:
        for emotion in emotion_manager.get_emotion_list():
            keywords = emotion_manager.get_keywords_for_emotion(emotion)
            emotion_weight = emotion_manager.get_emotion_weight(emotion)
            
            for keyword in keywords:
                repeat_count = text_lower.count(keyword.lower())
                if repeat_count > 1:
                    bonus_score = int(repeat_count * 0.5) * emotion_weight
                    emotion_scores[emotion] += bonus_score
    
    # Filter out zero scores
    return {emotion: score for emotion, score in emotion_scores.items() if score > 0}


def audio_to_data(audio_file_path, is_opus=True):
    # 获取文件后缀名
    file_type = os.path.splitext(audio_file_path)[1]
    if file_type:
        file_type = file_type.lstrip(".")
    # 读取音频文件，-nostdin 参数：不要从标准输入读取数据，否则FFmpeg会阻塞
    audio = AudioSegment.from_file(
        audio_file_path, format=file_type, parameters=["-nostdin"]
    )

    # 转换为单声道/16kHz采样率/16位小端编码（确保与编码器匹配）
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    # 音频时长(秒)
    duration = len(audio) / 1000.0

    # 获取原始PCM数据（16位小端）
    raw_data = audio.raw_data
    return pcm_to_data(raw_data, is_opus), duration


def audio_bytes_to_data(audio_bytes, file_type, is_opus=True):
    """
    直接用音频二进制数据转为opus/pcm数据，支持wav、mp3、p3
    """
    if file_type == "p3":
        # 直接用p3解码
        return p3.decode_opus_from_bytes(audio_bytes)
    else:
        # 其他格式用pydub
        audio = AudioSegment.from_file(
            BytesIO(audio_bytes), format=file_type, parameters=["-nostdin"]
        )
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        duration = len(audio) / 1000.0
        raw_data = audio.raw_data
        return pcm_to_data(raw_data, is_opus), duration


def pcm_to_data(raw_data, is_opus=True):
    # 初始化Opus编码器
    encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)

    # 编码参数
    frame_duration = 60  # 60ms per frame
    frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

    datas = []
    # 按帧处理所有音频数据（包括最后一帧可能补零）
    for i in range(0, len(raw_data), frame_size * 2):  # 16bit=2bytes/sample
        # 获取当前帧的二进制数据
        chunk = raw_data[i : i + frame_size * 2]

        # 如果最后一帧不足，补零
        if len(chunk) < frame_size * 2:
            chunk += b"\x00" * (frame_size * 2 - len(chunk))

        if is_opus:
            # 转换为numpy数组处理
            np_frame = np.frombuffer(chunk, dtype=np.int16)
            # 编码Opus数据
            frame_data = encoder.encode(np_frame.tobytes(), frame_size)
        else:
            frame_data = chunk if isinstance(chunk, bytes) else bytes(chunk)

        datas.append(frame_data)

    return datas


def opus_datas_to_wav_bytes(opus_datas, sample_rate=16000, channels=1):
    """
    将opus帧列表解码为wav字节流
    """
    decoder = opuslib_next.Decoder(sample_rate, channels)
    pcm_datas = []

    frame_duration = 60  # ms
    frame_size = int(sample_rate * frame_duration / 1000)  # 960

    for opus_frame in opus_datas:
        # 解码为PCM（返回bytes，2字节/采样点）
        pcm = decoder.decode(opus_frame, frame_size)
        pcm_datas.append(pcm)

    pcm_bytes = b"".join(pcm_datas)

    # 写入wav字节流
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return wav_buffer.getvalue()


def check_vad_update(before_config, new_config):
    if (
        new_config.get("selected_module") is None
        or new_config["selected_module"].get("VAD") is None
    ):
        return False
    update_vad = False
    current_vad_module = before_config["selected_module"]["VAD"]
    new_vad_module = new_config["selected_module"]["VAD"]
    current_vad_type = (
        current_vad_module
        if "type" not in before_config["VAD"][current_vad_module]
        else before_config["VAD"][current_vad_module]["type"]
    )
    new_vad_type = (
        new_vad_module
        if "type" not in new_config["VAD"][new_vad_module]
        else new_config["VAD"][new_vad_module]["type"]
    )
    update_vad = current_vad_type != new_vad_type
    return update_vad


def check_asr_update(before_config, new_config):
    if (
        new_config.get("selected_module") is None
        or new_config["selected_module"].get("ASR") is None
    ):
        return False
    update_asr = False
    current_asr_module = before_config["selected_module"]["ASR"]
    new_asr_module = new_config["selected_module"]["ASR"]
    current_asr_type = (
        current_asr_module
        if "type" not in before_config["ASR"][current_asr_module]
        else before_config["ASR"][current_asr_module]["type"]
    )
    new_asr_type = (
        new_asr_module
        if "type" not in new_config["ASR"][new_asr_module]
        else new_config["ASR"][new_asr_module]["type"]
    )
    update_asr = current_asr_type != new_asr_type
    return update_asr


def filter_sensitive_info(config: dict) -> dict:
    """
    过滤配置中的敏感信息
    Args:
        config: 原始配置字典
    Returns:
        过滤后的配置字典
    """
    sensitive_keys = [
        "api_key",
        "personal_access_token",
        "access_token",
        "token",
        "secret",
        "access_key_secret",
        "secret_key",
    ]

    def _filter_dict(d: dict) -> dict:
        filtered = {}
        for k, v in d.items():
            if any(sensitive in k.lower() for sensitive in sensitive_keys):
                filtered[k] = "***"
            elif isinstance(v, dict):
                filtered[k] = _filter_dict(v)
            elif isinstance(v, list):
                filtered[k] = [_filter_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                filtered[k] = v
        return filtered

    return _filter_dict(copy.deepcopy(config))


def get_vision_url(config: dict) -> str:
    """获取 vision URL

    Args:
        config: 配置字典

    Returns:
        str: vision URL
    """
    server_config = config["server"]
    vision_explain = server_config.get("vision_explain", "")
    if "你的" in vision_explain:
        local_ip = get_local_ip()
        port = int(server_config.get("http_port", 8003))
        vision_explain = f"http://{local_ip}:{port}/mcp/vision/explain"
    return vision_explain


def is_valid_image_file(file_data: bytes) -> bool:
    """
    检查文件数据是否为有效的图片格式

    Args:
        file_data: 文件的二进制数据

    Returns:
        bool: 如果是有效的图片格式返回True，否则返回False
    """
    # 常见图片格式的魔数（文件头）
    image_signatures = {
        b"\xff\xd8\xff": "JPEG",
        b"\x89PNG\r\n\x1a\n": "PNG",
        b"GIF87a": "GIF",
        b"GIF89a": "GIF",
        b"BM": "BMP",
        b"II*\x00": "TIFF",
        b"MM\x00*": "TIFF",
        b"RIFF": "WEBP",
    }

    # 检查文件头是否匹配任何已知的图片格式
    for signature in image_signatures:
        if file_data.startswith(signature):
            return True

    return False


def sanitize_tool_name(name: str) -> str:
    """Sanitize tool names for OpenAI compatibility."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)
