delete from sys_params where id in (700,701);
INSERT INTO `sys_params` (id, param_code, param_value, value_type, param_type, remark) VALUES (700, 'beian_icp_num', 'null', 'string', 1, 'ipc备案号，填写null则不设置');
INSERT INTO `sys_params` (id, param_code, param_value, value_type, param_type, remark) VALUES (701, 'beian_ga_num', 'null', 'string', 1, '公安备案号，填写null则不设置');
