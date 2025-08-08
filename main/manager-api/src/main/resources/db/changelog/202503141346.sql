-- Model Provider Table
DROP TABLE IF EXISTS `ai_model_provider`;
CREATE TABLE `ai_model_provider` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Primary key',
    `model_type` VARCHAR(20) COMMENT 'Model type (Memory/ASR/VAD/LLM/TTS)',
    `provider_code` VARCHAR(50) COMMENT 'Provider type',
    `name` VARCHAR(50) COMMENT 'Provider name',
    `fields` JSON COMMENT 'Provider fields (JSON format)',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT 'Sort order',
    `creator` BIGINT COMMENT 'Creator ID',
    `create_date` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `update_date` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`),
    INDEX `idx_ai_model_provider_model_type` (`model_type`) COMMENT 'Index for model type to quickly find all providers of a specific type'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Model provider table';

-- Model Configuration Table
DROP TABLE IF EXISTS `ai_model_config`;
CREATE TABLE `ai_model_config` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Primary key',
    `model_type` VARCHAR(20) COMMENT 'Model type (Memory/ASR/VAD/LLM/TTS)',
    `model_code` VARCHAR(50) COMMENT 'Model code (e.g. AliLLM, DoubaoTTS)',
    `model_name` VARCHAR(50) COMMENT 'Model name',
    `is_default` TINYINT(1) DEFAULT 0 COMMENT 'Is default config (0=No 1=Yes)',
    `is_enabled` TINYINT(1) DEFAULT 0 COMMENT 'Is enabled (0=No 1=Yes)',
    `config_json` JSON COMMENT 'Model configuration (JSON format)',
    `doc_link` VARCHAR(200) COMMENT 'Official documentation URL',
    `remark` VARCHAR(255) COMMENT 'Remarks',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT 'Sort order',
    `creator` BIGINT COMMENT 'Creator ID',
    `create_date` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `update_date` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`),
    INDEX `idx_ai_model_config_model_type` (`model_type`) COMMENT 'Index for model type to quickly find all configurations of a specific type'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Model configuration table';

-- TTS Voice Table
DROP TABLE IF EXISTS `ai_tts_voice`;
CREATE TABLE `ai_tts_voice` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Primary key',
    `tts_model_id` VARCHAR(32) COMMENT 'Corresponding TTS model ID',
    `name` VARCHAR(20) COMMENT 'Voice name',
    `tts_voice` VARCHAR(50) COMMENT 'Voice code',
    `languages` VARCHAR(50) COMMENT 'Languages supported',
    `voice_demo` VARCHAR(500) DEFAULT NULL COMMENT 'Voice demo',
    `remark` VARCHAR(255) COMMENT 'Remarks',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT 'Sort order',
    `creator` BIGINT COMMENT 'Creator ID',
    `create_date` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `update_date` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`),
    INDEX `idx_ai_tts_voice_tts_model_id` (`tts_model_id`) COMMENT 'Index for TTS model ID to quickly find voice information for corresponding model'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='TTS voice table';

-- Agent Template Table
DROP TABLE IF EXISTS `ai_agent_template`;
CREATE TABLE `ai_agent_template` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Agent unique identifier',
    `agent_code` VARCHAR(36) COMMENT 'Agent code',
    `agent_name` VARCHAR(64) COMMENT 'Agent name',
    `asr_model_id` VARCHAR(32) COMMENT 'Speech recognition model ID',
    `vad_model_id` VARCHAR(64) COMMENT 'Voice activity detection ID',
    `llm_model_id` VARCHAR(32) COMMENT 'Large language model ID',
    `tts_model_id` VARCHAR(32) COMMENT 'Text-to-speech model ID',
    `tts_voice_id` VARCHAR(32) COMMENT 'Voice ID',
    `mem_model_id` VARCHAR(32) COMMENT 'Memory model ID',
    `intent_model_id` VARCHAR(32) COMMENT 'Intent model ID',
    `system_prompt` TEXT COMMENT 'Role setting parameters',
    `lang_code` VARCHAR(10) COMMENT 'Language code',
    `language` VARCHAR(10) COMMENT 'Interaction language',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT 'Sort weight',
    `creator` BIGINT COMMENT 'Creator ID',
    `created_at` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `updated_at` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent template table';

-- Agent Configuration Table
DROP TABLE IF EXISTS `ai_agent`;
CREATE TABLE `ai_agent` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Agent unique identifier',
    `user_id` BIGINT COMMENT 'Owner user ID',
    `agent_code` VARCHAR(36) COMMENT 'Agent code',
    `agent_name` VARCHAR(64) COMMENT 'Agent name',
    `asr_model_id` VARCHAR(32) COMMENT 'Speech recognition model ID',
    `vad_model_id` VARCHAR(64) COMMENT 'Voice activity detection ID',
    `llm_model_id` VARCHAR(32) COMMENT 'Large language model ID',
    `tts_model_id` VARCHAR(32) COMMENT 'Text-to-speech model ID',
    `tts_voice_id` VARCHAR(32) COMMENT 'Voice ID',
    `mem_model_id` VARCHAR(32) COMMENT 'Memory model ID',
    `intent_model_id` VARCHAR(32) COMMENT 'Intent model ID',
    `system_prompt` TEXT COMMENT 'Role setting parameters',
    `lang_code` VARCHAR(10) COMMENT 'Language code',
    `language` VARCHAR(10) COMMENT 'Interaction language',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT 'Sort weight',
    `creator` BIGINT COMMENT 'Creator ID',
    `created_at` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `updated_at` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`),
    INDEX `idx_ai_agent_user_id` (`user_id`) COMMENT 'Index for user ID to quickly find agents under a user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent configuration table';

-- Device Information Table
DROP TABLE IF EXISTS `ai_device`;
CREATE TABLE `ai_device` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Device unique identifier',
    `user_id` BIGINT COMMENT 'Associated user ID',
    `mac_address` VARCHAR(50) COMMENT 'MAC address',
    `last_connected_at` DATETIME COMMENT 'Last connection time',
    `auto_update` TINYINT UNSIGNED DEFAULT 0 COMMENT 'Auto-update switch (0=Off/1=On)',
    `board` VARCHAR(50) COMMENT 'Device hardware model',
    `alias` VARCHAR(64) DEFAULT NULL COMMENT 'Device alias',
    `agent_id` VARCHAR(32) COMMENT 'Agent ID',
    `app_version` VARCHAR(20) COMMENT 'Firmware version',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT 'Sort order',
    `creator` BIGINT COMMENT 'Creator ID',
    `create_date` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `update_date` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`),
    INDEX `idx_ai_device_created_at` (`mac_address`) COMMENT 'Index for MAC address to quickly find device information'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Device information table';

-- Voiceprint Recognition Table
DROP TABLE IF EXISTS `ai_voiceprint`;
CREATE TABLE `ai_voiceprint` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Voiceprint unique identifier',
    `name` VARCHAR(64) COMMENT 'Voiceprint name',
    `user_id` BIGINT COMMENT 'User ID (associated with user table)',
    `agent_id` VARCHAR(32) COMMENT 'Associated agent ID',
    `agent_code` VARCHAR(36) COMMENT 'Associated agent code',
    `agent_name` VARCHAR(36) COMMENT 'Associated agent name',
    `description` VARCHAR(255) COMMENT 'Voiceprint description',
    `embedding` LONGTEXT COMMENT 'Voiceprint feature vector (JSON array format)',
    `memory` TEXT COMMENT 'Associated memory data',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT 'Sort weight',
    `creator` BIGINT COMMENT 'Creator ID',
    `created_at` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `updated_at` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Voiceprint recognition table';

-- Conversation History Table
DROP TABLE IF EXISTS `ai_chat_history`;
CREATE TABLE `ai_chat_history` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Conversation ID',
    `user_id` BIGINT COMMENT 'User ID',
    `agent_id` VARCHAR(32) DEFAULT NULL COMMENT 'Chat role',
    `device_id` VARCHAR(32) DEFAULT NULL COMMENT 'Device ID',
    `message_count` INT COMMENT 'Message summary',
    `creator` BIGINT COMMENT 'Creator ID',
    `create_date` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `update_date` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Conversation history table';

-- Conversation Message Table
DROP TABLE IF EXISTS `ai_chat_message`;
CREATE TABLE `ai_chat_message` (
    `id` VARCHAR(32) NOT NULL COMMENT 'Message unique identifier',
    `user_id` BIGINT COMMENT 'User unique identifier',
    `chat_id` VARCHAR(64) COMMENT 'Conversation history ID',
    `role` ENUM('user', 'assistant') COMMENT 'Role (user or assistant)',
    `content` TEXT COMMENT 'Message content',
    `prompt_tokens` INT UNSIGNED DEFAULT 0 COMMENT 'Prompt token count',
    `total_tokens` INT UNSIGNED DEFAULT 0 COMMENT 'Total token count',
    `completion_tokens` INT UNSIGNED DEFAULT 0 COMMENT 'Completion token count',
    `prompt_ms` INT UNSIGNED DEFAULT 0 COMMENT 'Prompt time (ms)',
    `total_ms` INT UNSIGNED DEFAULT 0 COMMENT 'Total time (ms)',
    `completion_ms` INT UNSIGNED DEFAULT 0 COMMENT 'Completion time (ms)',
    `creator` BIGINT COMMENT 'Creator ID',
    `create_date` DATETIME COMMENT 'Creation time',
    `updater` BIGINT COMMENT 'Updater ID',
    `update_date` DATETIME COMMENT 'Update time',
    PRIMARY KEY (`id`),
    INDEX `idx_ai_chat_message_user_id_chat_id_role` (`user_id`, `chat_id`) COMMENT 'Composite index for user ID, conversation ID and role to quickly retrieve messages',
    INDEX `idx_ai_chat_message_created_at` (`create_date`) COMMENT 'Index for creation time to sort or retrieve messages by time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Conversation message table';