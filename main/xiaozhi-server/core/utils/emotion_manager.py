import yaml
import os
from typing import Dict, List, Optional, Any
from loguru import logger

class EmotionManager:
    def __init__(self, config_path: str = "config/emotions.yaml"):
        self.config_path = config_path
        self.emotions = {}
        self.emoji_map = {}
        self.default_emotion = "neutral"
        self.load_emotions()
    
    def load_emotions(self):
        """Load emotion configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    
                self.emotions = config.get('emotions', {})
                self.default_emotion = config.get('default_emotion', 'neutral')
                
                # Load emotion persistence settings
                self.persistence_config = config.get('emotion_persistence', {
                    'enabled': True,
                    'llm_base_score': 5.0,
                    'half_life_chunks': 3.0,
                    'minimum_score': 0.1,
                    'keyword_multiplier': 1.0,
                    'llm_multiplier': 1.0
                })
                
                # Build emoji map for backward compatibility
                self.emoji_map = {
                    emotion: data.get('emoji', '🙂') 
                    for emotion, data in self.emotions.items()
                }
                
                logger.info(f"Loaded {len(self.emotions)} emotions from {self.config_path}")
            else:
                logger.warning(f"Emotion config file not found: {self.config_path}")
                self._create_default_config()
                
        except Exception as e:
            logger.error(f"Error loading emotion config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default emotion configuration"""
        self.emotions = {
            "bell": {"emoji": "🔔", "description": "默认情感"},
        }
        self.emoji_map = {"bell": "🔔"}
        self.default_emotion = "neutral"
    
    def get_emoji(self, emotion: str) -> str:
        """Get emoji for given emotion"""
        if emotion == self.default_emotion:
            # Return neutral emoji for default emotion
            logger.info(f"🔄 Using default emotion '{emotion}' -> 🙂")
            return "🙂"
        
        emoji = self.emoji_map.get(emotion, "🙂")
        if emotion in self.emoji_map:
            logger.debug(f"✅ Found emotion '{emotion}' mapped to emoji: {emoji}")
        else:
            logger.info(f"⚠️ Emotion '{emotion}' not found, using default emoji: 🙂")
        return emoji
    
    def get_emotion_list(self) -> List[str]:
        """Get list of available emotions"""
        return list(self.emotions.keys())
    
    def get_emotion_descriptions(self) -> Dict[str, str]:
        """Get emotion descriptions for prompt generation"""
        return {
            emotion: data.get('description', '') 
            for emotion, data in self.emotions.items()
        }
    
    def get_emotion_weight(self, emotion: str) -> float:
        """Get weight for given emotion (default: 1.0)"""
        if emotion in self.emotions:
            weight = self.emotions[emotion].get('weight', 1.0)
            return float(weight) if isinstance(weight, (int, float)) else 1.0
        return 1.0
    
    def get_all_emotion_weights(self) -> Dict[str, float]:
        """Get all emotion weights for scoring"""
        weights = {}
        for emotion, data in self.emotions.items():
            if isinstance(data, dict):
                weight = data.get('weight', 1.0)
                weights[emotion] = float(weight) if isinstance(weight, (int, float)) else 1.0
            else:
                weights[emotion] = 1.0
        return weights
    
    def get_persistence_config(self) -> Dict[str, Any]:
        """Get emotion persistence configuration"""
        return self.persistence_config.copy()
    
    def is_persistence_enabled(self) -> bool:
        """Check if emotion persistence is enabled"""
        return self.persistence_config.get('enabled', True)
    
    def generate_emotion_prompt(self) -> str:
        """Generate emotion detection prompt from configuration"""
        descriptions = self.get_emotion_descriptions()
        emotion_list = "\n".join([f"- {emotion}: {desc}" for emotion, desc in descriptions.items()])
        
        return f"""
除了意图识别，你还需要分析用户的情感状态。可用的情感类型包括：
{emotion_list}

请根据用户的语气、语境和对话内容来判断最合适的情感。如果无法确定具体情感，使用默认的 "{self.default_emotion}"。

返回格式示例：
```json
{{"function_call": {{"name": "continue_chat"}}, "emotion": "{self.default_emotion}"}}
```
"""

    def get_keywords_for_emotion(self, emotion: str) -> List[str]:
        """Get keywords for a specific emotion"""
        emotion_data = self.emotions.get(emotion, {})
        keywords = emotion_data.get('keywords', [])
        return keywords if isinstance(keywords, list) else []

# Global emotion manager instance
emotion_manager = EmotionManager()
