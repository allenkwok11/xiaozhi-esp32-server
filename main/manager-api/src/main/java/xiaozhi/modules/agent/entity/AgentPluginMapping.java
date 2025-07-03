package xiaozhi.modules.agent.entity;

import java.io.Serializable;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Agent与插件的唯一映射表
 * 
 * @TableName ai_agent_plugin_mapping
 */
@Data
@TableName(value = "ai_agent_plugin_mapping")
@Schema(description = " Unique mapping table between agent and plugin")
public class AgentPluginMapping implements Serializable {
    /**
     * 主键
     */
    @TableId(type = IdType.ASSIGN_ID)
    @Schema(description = "Mapping Info prymary key ID")
    private Long id;

    /**
     * 智能体ID
     */
    @Schema(description = "Agent ID")
    private String agentId;

    /**
     * 插件ID
     */
    @Schema(description = "Plugin ID")
    private String pluginId;

    /**
     * 插件参数(Json)格式
     */
    @Schema(description = "Plugin Parameter (Json) Format")
    private String paramInfo;

    // 冗余字段，用于方便在根据id查询插件时，对照查出插件的Provider_code,详见dao层xml文件
    @TableField(exist = false)
    @Schema(description = "Plugin provider_code, Mapping Table ai_model_provider")
    private String providerCode;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}