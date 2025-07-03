package xiaozhi.modules.agent.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 智能体记忆更新DTO
 */
@Data
@Schema(description = "智能体记忆更新对象")
public class AgentMemoryDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "Summary memory", example = "Build a scalable dynamic memory network that retains key information within limited space while intelligently maintaining the evolution of information.\n" +
"Summarize important user information based on conversation history to provide more personalized services in future interactions.", required = false)
    private String summaryMemory;
}