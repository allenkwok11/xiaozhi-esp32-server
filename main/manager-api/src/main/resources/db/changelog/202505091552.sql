-- 更新模型供应器表
UPDATE `ai_model_provider` SET fields = '[{"key": "host", "type": "string", "label": "服务地址"}, {"key": "port", "type": "number", "label": "端口号"}, {"key": "api_key", "type": "string", "label": "API密钥"}]' WHERE id = 'SYSTEM_ASR_FunASRServer';

-- 更新模型配置表
UPDATE `ai_model_config` SET config_json = '{"host": "127.0.0.1", "port": 10096, "type": "fun_server", "api_key": "none"}' WHERE id = 'ASR_FunASRServer';