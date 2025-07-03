package xiaozhi.modules.agent.dto;

import java.util.Date;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 智能体数据传输对象
 * 用于在服务层和控制器层之间传递智能体相关的数据
 */
@Data
@Schema(description = "Agent Object")
public class AgentDTO {
    @Schema(description = "Agent Code", example = "AGT_1234567890")
    private String id;

    @Schema(description = "Agent Name", example = "Customer Service Assistant")
    private String agentName;

    @Schema(description = "TTS model Name", example = "tts_model_01")
    private String ttsModelName;

    @Schema(description = "Timbre Name", example = "voice_01")
    private String ttsVoiceName;

    @Schema(description = "LLM Model Name", example = "llm_model_01")
    private String llmModelName;

    @Schema(description = "Memory Model Name", example = "vllm_model_01")
    private String vllmModelName;

    @Schema(description = "Memory Model ID", example = "mem_model_01")
    private String memModelId;

    @Schema(description = " Role Setting parameter", example = "You are a professional customer support assistant, responsible for answering user questions and providing assistance. ")
    private String systemPrompt;

    @Schema(description = "Summary memory", example = "Build a scalable dynamic memory network that retains key information within limited space while intelligently maintaining the evolution of information.\n" +
"Summarize important user information based on conversation history to provide more personalized services in future interactions.", required = false)
    private String summaryMemory;

    @Schema(description = "Last Connect Time", example = "2024-03-20 10:00:00")
    private Date lastConnectedAt;

    @Schema(description = "Device Number", example = "10")
    private Integer deviceCount;
}