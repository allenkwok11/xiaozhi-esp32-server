package xiaozhi.common.constant;

/**
 * 常量
 * Copyright (c) 人人开源 All rights reserved.
 * Website: https://www.renren.io
 */
public interface Constant {
    /**
     * 成功
     */
    int SUCCESS = 1;
    /**
     * 失败
     */
    int FAIL = 0;
    /**
     * OK
     */
    String OK = "OK";
    /**
     * 用户标识
     */
    String USER_KEY = "userId";
    /**
     * 菜单根节点标识
     */
    Long MENU_ROOT = 0L;
    /**
     * 部门根节点标识
     */
    Long DEPT_ROOT = 0L;
    /**
     * 数据字典根节点标识
     */
    Long DICT_ROOT = 0L;
    /**
     * 升序
     */
    String ASC = "asc";
    /**
     * 降序
     */
    String DESC = "desc";
    /**
     * 创建时间字段名
     */
    String CREATE_DATE = "create_date";

    /**
     * 创建时间字段名
     */
    String ID = "id";

    /**
     * 数据权限过滤
     */
    String SQL_FILTER = "sqlFilter";

    /**
     * 当前页码
     */
    String PAGE = "page";
    /**
     * 每页显示记录数
     */
    String LIMIT = "limit";
    /**
     * 排序字段
     */
    String ORDER_FIELD = "orderField";
    /**
     * 排序方式
     */
    String ORDER = "order";

    /**
     * 请求头授权标识
     */
    String AUTHORIZATION = "Authorization";

    /**
     * 服务器密钥
     */
    String SERVER_SECRET = "server.secret";

    /**
     * websocket地址
     */
    String SERVER_WEBSOCKET = "server.websocket";

    /**
     * ota地址
     */
    String SERVER_OTA = "server.ota";

    /**
     * 是否允许用户注册
     */
    String SERVER_ALLOW_USER_REGISTER = "server.allow_user_register";

    /**
     * 下发六位验证码时显示的控制面板地址
     */
    String SERVER_FRONTED_URL = "server.fronted_url";

    /**
     * 路径分割符
     */
    String FILE_EXTENSION_SEG = ".";

    enum SysBaseParam {
        /**
         * 系统全称
         */
        SYS_NAME("SYS_NAME"),
        /**
         * 系统简称
         */
        SYS_SHORT_NAME("SYS_SHORT_NAME"),
        /**
         * 系统描述
         */
        SYS_DES("SYS_DES"),
        /**
         * 登录失败几次锁定
         */
        LOGIN_LOCK_COUNT("LOGIN_LOCK_COUNT"),
        /**
         * 账号失败锁定分钟数
         */
        LOGIN_LOCK_TIME("LOGIN_LOCK_TIME"),
        /**
         * TOKEN强验证
         */
        SYS_TOKEN_SECURITY("SYS_TOKEN_SECURITY");

        private String value;

        SysBaseParam(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    /**
     * 系统短信
     */
    enum SysMSMParam {
        /**
         * 阿里云授权keyID
         */
        ALIYUN_SMS_ACCESS_KEY_ID("aliyun.sms.access_key_id"),
        /**
         * 阿里云授权密钥
         */
        ALIYUN_SMS_ACCESS_KEY_SECRET("aliyun.sms.access_key_secret"),
        /**
         *
         */
        ALIYUN_SMS_SIGN_NAME("aliyun.sms.sign_name"),
        /**
         * 已删除
         */
        ALIYUN_SMS_SMS_CODE_TEMPLATE_CODE("aliyun.sms.sms_code_template_code"),
        /**
         * 已删除
         */
        SYSTEM_SMS_MAX_SEND_COUNT("system.sms.max_send_count"),
        /**
         * 是否开启手机注册
         */
        SYSTEM_ENABLE_MOBILE_REGISTER("system.enable_mobile_register");

        private String value;

        SysMSMParam(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    /**
     * 数据状态
     */
    enum DataOperation {
        /**
         * 插入
         */
        INSERT("I"),
        /**
         * 已修改
         */
        UPDATE("U"),
        /**
         * 已删除
         */
        DELETE("D");

        private String value;

        DataOperation(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    /**
     * 版本号
     */
    public static final String VERSION = "0.4.2";
}