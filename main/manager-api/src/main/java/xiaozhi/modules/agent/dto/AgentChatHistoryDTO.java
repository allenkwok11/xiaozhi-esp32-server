package xiaozhi.modules.agent.dto;

import java.util.Date;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 智能体聊天记录DTO
 */
@Data
@Schema(description = "智能体聊天记录 Agent Chat History")
public class AgentChatHistoryDTO {
    @Schema(description = "Created Date")
    private Date createdAt;

    @Schema(description = "Message Type: 1-user, 2-Agent")
    private Byte chatType;

    @Schema(description = "Chat Content")
    private String content;

    @Schema(description = "Audio ID")
    private String audioId;

    @Schema(description = "MAC Address")
    private String macAddress;
}