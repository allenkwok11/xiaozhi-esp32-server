'''google.py'''

import logging
import os
from typing import Optional
from google.cloud import texttospeech
from core.providers.tts.base import TTSProviderBase

TAG = __name__
logger = logging.getLogger(TAG)

class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.client = texttospeech.TextToSpeechClient()
        self.language_code = config.get("language_code", "en-US")
        self.voice_name = config.get("voice_name", "en-US-Standard-B")
        self.speaking_rate = config.get("speaking_rate", 1.0)
        self.pitch = config.get("pitch", 0.0)

    async def text_to_speak(self, text, output_file):
        logger.info(f"[GoogleTTS] text_to_speak called with text: {text[:100]}... output_file: {output_file}")
        try:
            input_text = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=self.language_code,
                name=self.voice_name
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=self.speaking_rate,
                pitch=self.pitch
            )
            logger.info(f"[GoogleTTS] Requesting synthesis: lang={self.language_code}, voice={self.voice_name}, rate={self.speaking_rate}, pitch={self.pitch}")
            response = self.client.synthesize_speech(
                input=input_text,
                voice=voice,
                audio_config=audio_config
            )
            logger.info(f"[GoogleTTS] Synthesis response received. Audio size: {len(response.audio_content)} bytes")
            if output_file:
                with open(output_file, "wb") as out:
                    out.write(response.audio_content)
                logger.info(f"[GoogleTTS] Audio content written to file {output_file}")
                return output_file
            else:
                logger.info(f"[GoogleTTS] Returning audio bytes directly.")
                return response.audio_content
        except Exception as e:
            logger.error(f"[GoogleTTS] Error in text_to_speak: {e}", exc_info=True)
            raise

    def set_voice(self, language_code, voice_name):
        self.language_code = language_code
        self.voice_name = voice_name

    def set_speaking_rate(self, rate):
        self.speaking_rate = rate

    def set_pitch(self, pitch):
        self.pitch = pitch
