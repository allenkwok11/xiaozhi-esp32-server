package xiaozhi.modules.device.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 设备信息表
 * @TableName ai_device
 */
@TableName(value ="ai_device")
@Data
public class Device implements Serializable {
    /**
     * 设备唯一标识
     */
    @TableId
    private String id;

    /**
     * 关联用户 ID
     */
    private Long userId;

    /**
     * MAC 地址
     */
    private String macAddress;

    /**
     * 最后连接时间
     */
    private Date lastConnectedAt;

    /**
     * 自动更新开关(0 关闭/1 开启)
     */
    private Integer autoUpdate;

    /**
     * 设备硬件型号
     */
    private String board;

    /**
     * 设备别名
     */
    private String alias;

    /**
     * 智能体 ID
     */
    private String agentId;

    /**
     * 固件版本号
     */
    private String appVersion;

    /**
     * 排序
     */
    private Integer sort;

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