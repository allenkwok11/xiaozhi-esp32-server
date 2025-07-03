package xiaozhi.modules.agent.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 智能体创建DTO
 * 专用于新增智能体，不包含id、agentCode和sort字段，这些字段由系统自动生成/设置默认值
 */
@Data
@Schema(description = "Agent create Object")
public class AgentCreateDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "Agent Name", example = "Customer Service Asssistant")
    @NotBlank(message = "Agent name cannot be empty")
    private String agentName;
}