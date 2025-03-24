package xiaozhi.modules.agent.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 智能体配置模板表
 * @TableName ai_agent_template
 */
@TableName(value ="ai_agent_template")
@Data
public class AgentTemplate implements Serializable {
    /**
     * 智能体唯一标识
     */
    @TableId
    private String id;

    /**
     * 智能体编码
     */
    private String agentCode;

    /**
     * 智能体名称
     */
    private String agentName;

    /**
     * 语音识别模型标识
     */
    private String asrModelId;

    /**
     * 语音活动检测标识
     */
    private String vadModelId;

    /**
     * 大语言模型标识
     */
    private String llmModelId;

    /**
     * 语音合成模型标识
     */
    private String ttsModelId;

    /**
     * 音色标识
     */
    private String ttsVoiceId;

    /**
     * 记忆模型标识
     */
    private String memModelId;

    /**
     * 意图模型标识
     */
    private String intentModelId;

    /**
     * 角色设定参数
     */
    private String systemPrompt;

    /**
     * 语言编码
     */
    private String langCode;

    /**
     * 交互语种
     */
    private String language;

    /**
     * 排序权重
     */
    private Integer sort;

    /**
     * 是否默认模板：1：是，0：不是
     */
    private Integer isDefault;

    /**
     * 创建者 ID
     */
    private Long creator;

    /**
     * 创建时间
     */
    private Date createdAt;

    /**
     * 更新者 ID
     */
    private Long updater;

    /**
     * 更新时间
     */
    private Date updatedAt;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}