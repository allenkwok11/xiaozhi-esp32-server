-- VLLM模型供应器
DELETE FROM `ai_model_provider` WHERE id = 'SYSTEM_VLLM_openai';
INSERT INTO `ai_model_provider` (`id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`) VALUES
('SYSTEM_VLLM_openai', 'VLLM', 'openai', 'OpenAI API', '[{"key":"base_url","label":"Base URL","type":"string"},{"key":"model_name","label":"Model Name","type":"string"},{"key":"api_key","label":"API Key","type":"string"}]', 9, 1, NOW(), 1, NOW());

-- VLLM Model Configuration
DELETE FROM `ai_model_config` WHERE id = 'VLLM_ChatGLMVLLM';
INSERT INTO `ai_model_config` VALUES ('VLLM_ChatGLMVLLM', 'VLLM', 'ChatGLMVLLM', 'Zhipu Vision AI', 1, 1, '{\"type\": \"openai\", \"model_name\": \"glm-4v-flash\", \"base_url\": \"https://open.bigmodel.cn/api/paas/v4/\", \"api_key\": \"your_api_key\"}', NULL, NULL, 1, NULL, NULL, NULL, NULL);
-- 更新文档
UPDATE `ai_model_config` SET 
`doc_link` = 'https://bigmodel.cn/usercenter/proj-mgmt/apikeys',
`remark` = '智谱视觉AI配置说明：
1. 访问 https://bigmodel.cn/usercenter/proj-mgmt/apikeys
2. 注册并获取API密钥
3. 填入配置文件中' WHERE `id` = 'VLLM_ChatGLMVLLM';


-- 添加参数
INSERT INTO `sys_params` (id, param_code, param_value, value_type, param_type, remark) VALUES (113, 'server.http_port', '8003', 'number', 1, 'HTTP service port for vision analysis API');
INSERT INTO `sys_params` (id, param_code, param_value, value_type, param_type, remark) VALUES (114, 'server.vision_explain', 'null', 'string', 1, 'Vision analysis API endpoint for device configuration, use ; to separate multiple endpoints ');

-- 智能体表增加VLLM模型配置
ALTER TABLE `ai_agent` 
ADD COLUMN `vllm_model_id` varchar(32) NULL DEFAULT 'VLLM_ChatGLMVLLM' COMMENT '视觉模型标识' AFTER `llm_model_id`;

-- 智能体模版表增加VLLM模型配置
ALTER TABLE `ai_agent_template` 
ADD COLUMN `vllm_model_id` varchar(32) NULL DEFAULT 'VLLM_ChatGLMVLLM' COMMENT '视觉模型标识' AFTER `llm_model_id`;