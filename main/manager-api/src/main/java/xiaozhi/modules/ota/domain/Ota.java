package xiaozhi.modules.ota.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * OTA升级信息表
 * @TableName ai_ota
 */
@TableName(value ="ai_ota")
@Data
public class Ota implements Serializable {
    /**
     * 记录唯一标识
     */
    @TableId
    private String id;

    /**
     * 设备硬件型号
     */
    private String board;

    /**
     * 固件版本号
     */
    private String appVersion;

    /**
     * 下载地址
     */
    private String url;

    /**
     * 是否启用
     */
    private Integer isEnabled;

    /**
     * 创建者
     */
    private Long creator;

    /**
     * 创建时间
     */
    private Date createDate;

    /**
     * 更新者
     */
    private Long updater;

    /**
     * 更新时间
     */
    private Date updateDate;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}