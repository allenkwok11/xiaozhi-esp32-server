package xiaozhi.modules.model.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * TTS 音色表
 * @TableName ai_tts_voice
 */
@TableName(value ="ai_tts_voice")
@Data
public class TtsVoice implements Serializable {
    /**
     * 主键
     */
    @TableId
    private String id;

    /**
     * 对应 TTS 模型主键
     */
    private String ttsModelId;

    /**
     * 音色名称
     */
    private String name;

    /**
     * 音色编码
     */
    private String ttsVoice;

    /**
     * 语言
     */
    private String languages;

    /**
     * 音色 Demo
     */
    private String voiceDemo;

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