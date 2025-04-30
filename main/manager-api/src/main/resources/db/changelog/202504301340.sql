update `ai_model_provider` set `fields` = 
'[{"key": "api_url","label": "API地址","type": "string"},{"key": "voice","label": "音色","type": "string"},{"key": "output_dir","label": "输出目录","type": "string"},{"key": "authorization","label": "授权","type": "string"},{"key": "appid","label": "应用ID","type": "string"},{"key": "access_token","label": "访问令牌","type": "string"},{"key": "cluster","label": "集群","type": "string"},{"key": "speed_ratio","label": "语速","type": "number"},{"key": "volume_ratio","label": "音量","type": "number"},{"key": "pitch_ratio","label": "音高","type": "number"}]'
where `id` = 'SYSTEM_TTS_doubao';

-- 添加阿里云ASR供应器
INSERT INTO `ai_model_provider` (`id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`) VALUES
('SYSTEM_ASR_AliyunASR', 'ASR', 'aliyun', '阿里云语音识别', '[{"key":"appkey","label":"应用AppKey","type":"string"},{"key":"token","label":"临时Token","type":"string"},{"key":"access_key_id","label":"AccessKey ID","type":"string"},{"key":"access_key_secret","label":"AccessKey Secret","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"}]', 5, 1, NOW(), 1, NOW());

-- 添加阿里云ASR模型配置
INSERT INTO `ai_model_config` VALUES ('ASR_AliyunASR', 'ASR', 'AliyunASR', '阿里云语音识别', 0, 1, '{\"type\": \"aliyun\", \"appkey\": \"\", \"token\": \"\", \"access_key_id\": \"\", \"access_key_secret\": \"\", \"output_dir\": \"tmp/\"}', NULL, NULL, 6, NULL, NULL, NULL, NULL);

-- 更新阿里云ASR模型配置的说明文档
UPDATE `ai_model_config` SET 
`doc_link` = 'https://nls-portal.console.aliyun.com/',
`remark` = '阿里云ASR配置说明：
1. 访问 https://nls-portal.console.aliyun.com/ 开通服务
2. 访问 https://nls-portal.console.aliyun.com/applist 获取appkey
3. 访问 https://nls-portal.console.aliyun.com/overview 获取token
4. 获取access_key_id和access_key_secret
5. 填入配置文件中' WHERE `id` = 'ASR_AliyunASR';
