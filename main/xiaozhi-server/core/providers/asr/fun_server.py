'''google.py'''
from config.logger import setup_logging
import time
import os
from google.cloud import speech
import pyaudio
from core.providers.asr.base import ASRProviderBase
import opuslib_next
from typing import List
import asyncio

TAG = __name__
logger = setup_logging()

class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        logger.bind(tag=TAG).debug("[Google STT] ASRProvider initialized")
        super().__init__()
        self.interface_type = "google"
        self.client = speech.SpeechClient()
        self.output_dir = config.get("output_dir", os.path.join(os.getcwd(), "output"))
        os.makedirs(self.output_dir, exist_ok=True)

    def init_pyaudio(self):
        return pyaudio.PyAudio()

    async def speech_to_text(self, opus_data, session_id, audio_format="opus"):
        """Convert Opus data to text using Google STT."""
        logger.bind(tag=TAG).debug(f"[Google STT] speech_to_text called with session_id: {session_id}")
        pcm_data = self.decode_opus(opus_data)
        file_path = self.save_audio_to_file([pcm_data], session_id)

        with open(file_path, "rb") as audio_file:
            audio_content = audio_file.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )

        response = self.client.recognize(config=config, audio=audio)

        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            return transcript, file_path
        else:
            return None, file_path

    def start_speech_to_text(self, client, py_audio):
        """Stream audio to Google STT and return transcript."""
        stream = py_audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        audio_generator = self._audio_stream_generator(stream)
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )

        streaming_config = speech.StreamingRecognitionConfig(config=config)

        responses = client.streaming_recognize(streaming_config, requests)

        for response in responses:
            for result in response.results:
                if result.is_final:
                    return result.alternatives[0].transcript, stream

    def stop_speech_to_text(self, stream):
        """Stop the audio stream."""
        stream.stop_stream()
        stream.close()

    def _audio_stream_generator(self, stream):
        """Generate audio chunks from the stream."""
        while True:
            yield stream.read(1024)

    @staticmethod
    def decode_opus(opus_data: List[bytes]) -> bytes:
        """Decode Opus data to PCM format."""
        try:
            decoder = opuslib_next.Decoder(16000, 1)  # 16kHz, mono
            pcm_data = []

            for opus_packet in opus_data:
                try:
                    pcm_frame = decoder.decode(opus_packet, 960)  # 960 samples per frame
                    if pcm_frame:
                        pcm_data.append(pcm_frame)
                except opuslib_next.OpusError as e:
                    logger.bind(tag=TAG).warning(f"Opus decoding error, skipping packet: {e}")
                    continue
                except Exception as e:
                    logger.bind(tag=TAG).error(f"Audio processing error: {e}", exc_info=True)
                    continue

            return b"".join(pcm_data)
        except Exception as e:
            logger.bind(tag=TAG).error(f"Error during audio decoding: {e}", exc_info=True)
            return b""

# Example usage
if __name__ == "__main__":
    # logger.bind(tag=TAG).debugging.basicConfig(level=logging.DEBUG)

    google_api = GoogleSTTProvider()
    py_audio = google_api.init_pyaudio()
    speech_client = google_api.client

    stream = None
    try:
        result = google_api.start_speech_to_text(speech_client, py_audio)
        if result is not None:
            user_input, stream = result
            logger.bind(tag=TAG).debug(f"Voice input: {user_input}")
        else:
            logger.bind(tag=TAG).error("No speech recognized.")
            stream = None
    except Exception as e:
        logger.bind(tag=TAG).error(f"Error during speech-to-text: {e}")
        stream = None
    finally:
        if stream is not None:
            google_api.stop_speech_to_text(stream)