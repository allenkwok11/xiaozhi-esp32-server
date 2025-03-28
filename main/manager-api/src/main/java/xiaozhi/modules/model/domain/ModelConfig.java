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
 * @TableName ai_model_config
 */
@TableName(value ="ai_model_config")
@Data
public class ModelConfig implements Serializable {
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
     * 模型编码(如AliLLM、DoubaoTTS)
     */
    private String modelCode;

    /**
     * 模型名称
     */
    private String modelName;

    /**
     * 是否默认配置(0否 1是)
     */
    private Integer isDefault;

    /**
     * 是否启用
     */
    private Integer isEnabled;

    /**
     * 模型配置(JSON格式)
     */
    private String configJson;

    /**
     * 官方文档链接
     */
    private String docLink;

    /**
     * 备注
     */
    private String remark;

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