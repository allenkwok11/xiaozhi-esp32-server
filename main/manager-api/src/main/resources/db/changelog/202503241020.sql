-- OTA升级信息表
DROP TABLE IF EXISTS `ai_ota`;
CREATE TABLE `ai_ota` (
    `id` VARCHAR(32) NOT NULL COMMENT '记录唯一标识',
    `board` VARCHAR(50) COMMENT '设备硬件型号',
    `app_version` VARCHAR(20) COMMENT '固件版本号',
    `url` VARCHAR(500) COMMENT '下载地址',
    `is_enabled` TINYINT(1) DEFAULT 0 COMMENT '是否启用',
    `creator` BIGINT COMMENT '创建者',
    `create_date` DATETIME COMMENT '创建时间',
    `updater` BIGINT COMMENT '更新者',
    `update_date` DATETIME COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uni_ai_ota_board` (`board`) COMMENT '设备型号唯一索引，用于快速查找升级信息'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OTA升级信息表';
