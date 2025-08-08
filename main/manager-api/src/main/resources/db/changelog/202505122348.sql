-- summarise memories
ALTER TABLE `ai_agent`
ADD COLUMN `summary_memory` text COMMENT 'summarise memories' AFTER `system_prompt`;

ALTER TABLE `ai_agent_template`
ADD COLUMN `summary_memory` text COMMENT 'summarise memories' AFTER `system_prompt`;
