package xiaozhi.modules.agent.entity;

import java.util.Date;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@TableName("ai_agent")
@Schema(description = "Agent information")
public class AgentEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "Unique agent identifier")
    private String id;

    @Schema(description = "Associated user ID")
    private Long userId;

    @Schema(description = "Agent code")
    private String agentCode;

    @Schema(description = "Agent name")
    private String agentName;

    @Schema(description = "ASR (Automatic Speech Recognition) model ID")
    private String asrModelId;

    @Schema(description = "VAD (Voice Activity Detection) model ID")
    private String vadModelId;

    @Schema(description = "LLM (Large Language Model) ID")
    private String llmModelId;

    @Schema(description = "VLLM model ID")
    private String vllmModelId;

    @Schema(description = "TTS (Text-to-Speech) model ID")
    private String ttsModelId;

    @Schema(description = "Timbre ID")
    private String ttsVoiceId;

    @Schema(description = "Memory model ID")
    private String memModelId;

    @Schema(description = "Intent model ID")
    private String intentModelId;

    @Schema(description = "Chat history configuration (0: do not record, 1: record text only, 2: record text and audio)")
    private Integer chatHistoryConf;

    @Schema(description = "Role setting parameters")
    private String systemPrompt;

    @Schema(description = "Summary memory", example = "Build a scalable dynamic memory network that retains key information within limited space while intelligently maintaining the evolution of information.\n" +
            "Summarize important user information based on conversation history to provide more personalized services in future interactions.", required = false)
    private String summaryMemory;

    @Schema(description = "Language code")
    private String langCode;

    @Schema(description = "Interaction language")
    private String language;

    @Schema(description = "Sort order")
    private Integer sort;

    @Schema(description = "Creator")
    private Long creator;

    @Schema(description = "Created at")
    private Date createdAt;

    @Schema(description = "Updater")
    private Long updater;

    @Schema(description = "Updated at")
    private Date updatedAt;
}