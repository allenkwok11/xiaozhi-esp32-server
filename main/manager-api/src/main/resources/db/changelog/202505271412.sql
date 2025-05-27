-- 本地短期记忆配置可以设置独立的LLM

update `ai_model_provider` set fields =  '[{"key":"llm","label":"LLM模型","type":"string"}]' where  id = 'SYSTEM_Memory_mem_local_short';
update `ai_model_config` set config_json =  '{\"type\": \"mem_local_short\", \"llm\": \"LLM_ChatGLMLLM\"}' where  id = 'Memory_mem_local_short';
