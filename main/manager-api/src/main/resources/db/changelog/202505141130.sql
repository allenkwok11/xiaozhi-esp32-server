-- 添加手机短信注册功能的需要的参数
delete from sys_params where id in (601, 602, 610, 611, 612, 613);
INSERT INTO sys_params
(id, param_code, param_value, value_type, param_type, remark, creator, create_date, updater, update_date)
    VALUES
(601, 'system.enable_mobile_register', 'false', 'boolean', 1, '是否开启手机注册', NULL, NULL, NULL, NULL),
(602, 'system.sms.max_send_count', '5', 'number', 1, '单号码最大短信发送条数', NULL, NULL, NULL, NULL),
(610, 'aliyun.sms.access_key_id', '', 'string', 1, '阿里云平台access_key', NULL, NULL, NULL, NULL),
(611, 'aliyun.sms.access_key_secret', '', 'string', 1, '阿里云平台access_key_secret', NULL, NULL, NULL, NULL),
(612, 'aliyun.sms.sign_name', '', 'string', 1, '阿里云短信签名', NULL, NULL, NULL, NULL),
(613, 'aliyun.sms.sms_code_template_code', '', 'string', 1, '阿里云短信模板', NULL, NULL, NULL, NULL);