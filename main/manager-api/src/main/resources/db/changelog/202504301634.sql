-- 初始化智能体聊天记录
DROP TABLE IF EXISTS ai_agent_chat_history;
CREATE TABLE ai_agent_chat_history
(
    id          BIGINT AUTO_INCREMENT COMMENT '主键ID'
        PRIMARY KEY,
    mac_address VARCHAR(50) COMMENT 'MAC地址',
    agent_id BIGINT DEFAULT 0 COMMENT '智能体id',
    session_id  VARCHAR(50) COMMENT '会话ID',
    sort        BIGINT COMMENT '排序值（与session_id对应），使用时间戳，方便排序',
    chat_type   TINYINT(3) COMMENT '消息类型: 1-用户, 2-智能体',
    content     VARCHAR(1024) COMMENT '聊天内容',
    audio       text         COMMENT '音频base64数据',
    audio_url   VARCHAR(256) COMMENT '音频URL',
    created_at  DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3) NOT NULL COMMENT '创建时间',
    updated_at  DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3) NOT NULL ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
    INDEX idx_mac_session (mac_address, sort)
) COMMENT '智能体聊天记录表';
