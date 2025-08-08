DROP TABLE IF EXISTS sys_user;
DROP TABLE IF EXISTS sys_params;
DROP TABLE IF EXISTS sys_user_token;
DROP TABLE IF EXISTS sys_dict_type;
DROP TABLE IF EXISTS sys_dict_data;

-- system user
CREATE TABLE sys_user (
  id bigint NOT NULL COMMENT 'id',
  username varchar(50) NOT NULL COMMENT 'user',
  password varchar(100) COMMENT 'password',
  super_admin tinyint unsigned COMMENT 'super_admin   0：no   1：yes',
  status tinyint COMMENT 'status  0：disabled   1：normal',
  create_date datetime COMMENT 'creation time',
  updater bigint COMMENT 'updater',
  creator bigint COMMENT 'creater',
  update_date datetime COMMENT 'update time',
  primary key (id),
  unique key uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='system user';

-- System user Tokens
CREATE TABLE sys_user_token (
  id bigint NOT NULL COMMENT 'id',
  user_id bigint NOT NULL COMMENT 'User id',
  token varchar(100) NOT NULL COMMENT 'User token',
  expire_date datetime COMMENT 'Expire time',
  update_date datetime COMMENT 'update time',
  create_date datetime COMMENT 'create time',
  PRIMARY KEY (id),
  UNIQUE KEY user_id (user_id),
  UNIQUE KEY token (token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='System user Token';

-- param management
create table sys_params
(
  id                   bigint NOT NULL COMMENT 'id',
  param_code           varchar(32) COMMENT 'parameter code',
  param_value          varchar(2000) COMMENT 'parameter value',
  param_type           tinyint unsigned default 1 COMMENT 'type   0：system param   1：non system param',
  remark               varchar(200) COMMENT 'remark',
  creator              bigint COMMENT 'creator',
  create_date          datetime COMMENT 'create time',
  updater              bigint COMMENT 'Updater',
  update_date          datetime COMMENT 'Update date',
  primary key (id),
  unique key uk_param_code (param_code)
)ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COMMENT='Parameter Management';

-- 字典类型
create table sys_dict_type
(
    id                   bigint NOT NULL COMMENT 'id',
    dict_type            varchar(100) NOT NULL COMMENT 'dict_type',
    dict_name            varchar(255) NOT NULL COMMENT 'dict_name',
    remark               varchar(255) COMMENT 'remark',
    sort                 int unsigned COMMENT 'sort',
    creator              bigint COMMENT 'creator',
    create_date          datetime COMMENT 'create_date',
    updater              bigint COMMENT 'updater',
    update_date          datetime COMMENT 'update_date',
    primary key (id),
    UNIQUE KEY(dict_type)
)ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COMMENT='dict_type';

-- 字典数据
create table sys_dict_data
(
    id                   bigint NOT NULL COMMENT 'id',
    dict_type_id         bigint NOT NULL COMMENT 'dict type ID',
    dict_label           varchar(255) NOT NULL COMMENT 'dict label',
    dict_value           varchar(255) COMMENT 'dict_value',
    remark               varchar(255) COMMENT 'remark',
    sort                 int unsigned COMMENT 'sort',
    creator              bigint COMMENT 'creator',
    create_date          datetime COMMENT 'create_date',
    updater              bigint COMMENT 'updater',
    update_date          datetime COMMENT 'Update_date',
    primary key (id),
    unique key uk_dict_type_value (dict_type_id, dict_value),
    key idx_sort (sort)
)ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COMMENT='dict type';