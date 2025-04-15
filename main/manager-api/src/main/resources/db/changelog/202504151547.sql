-- 修正CosyVoiceSiliconflow音色
delete from `ai_tts_voice` where tts_model_id = 'TTS_CosyVoiceSiliconflow';
INSERT INTO `ai_tts_voice` VALUES ('TTS_CosyVoiceSiliconflow0001', 'TTS_CosyVoiceSiliconflow', 'CosyVoice男声', 'FunAudioLLM/CosyVoice2-0.5B:alex', '中文', 'https://example.com/cosyvoice/alex.mp3', NULL, 6, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_CosyVoiceSiliconflow0002', 'TTS_CosyVoiceSiliconflow', 'CosyVoice女声', 'FunAudioLLM/CosyVoice2-0.5B:bella', '中文', 'https://example.com/cosyvoice/bella.mp3', NULL, 6, NULL, NULL, NULL, NULL);