-- 修改自定义TTS接口请求定义
update `ai_model_provider` set `fields` =
'[{"key":"url","label":"服务地址","type":"string"},{"key":"method","label":"请求方式","type":"string"},{"key":"params","label":"请求参数","type":"dict","dict_name":"params"},{"key":"headers","label":"请求头","type":"dict","dict_name":"headers"},{"key":"format","label":"音频格式","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"}]'
where `id` = 'SYSTEM_TTS_custom';