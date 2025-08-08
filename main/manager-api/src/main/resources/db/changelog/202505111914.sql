-- 添加聊天记录配置字段
ALTER TABLE `ai_agent` 
ADD COLUMN `chat_history_conf` tinyint NOT NULL DEFAULT 0 COMMENT 'Chat log configuration (0=no logging, 1=text only, 2=text and voice)' AFTER `system_prompt`;

ALTER TABLE `ai_agent_template` 
ADD COLUMN `chat_history_conf` tinyint NOT NULL DEFAULT 0 COMMENT 'Chat log configuration (0=no logging, 1=text only, 2=text and voice)' AFTER `system_prompt`;