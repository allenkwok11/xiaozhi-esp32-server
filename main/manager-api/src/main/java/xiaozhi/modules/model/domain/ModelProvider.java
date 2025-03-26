package xiaozhi.modules.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 模型配置表
 * @TableName ai_model_provider
 */
@TableName(value ="ai_model_provider")
@Data
public class ModelProvider implements Serializable {
    /**
     * 主键
     */
    @TableId
    private String id;

    /**
     * 模型类型(Memory/ASR/VAD/LLM/TTS)
     */
    private String modelType;

    /**
     * 供应器类型
     */
    private String providerCode;

    /**
     * 供应器名称
     */
    private String name;

    /**
     * 供应器字段列表(JSON格式)
     */
    private Object fields;

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