package xiaozhi.modules.agent.dto;

import java.io.Serializable;
import java.util.HashMap;
import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import xiaozhi.modules.agent.dto.AgentUpdateDTO.FunctionInfo;

/**
 * 智能体更新DTO
 * 专用于更新智能体，id字段是必需的，用于标识要更新的智能体
 * 其他字段均为非必填，只更新提供的字段
 */
@Data
@Schema(description = "Agent Update Object")
public class AgentUpdateDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "Agent Code", example = "AGT_1234567890", nullable = true)
    private String agentCode;

    @Schema(description = "Agent Name", example = "客服助手", nullable = true)
    private String agentName;

    @Schema(description = "ASR Model ID", example = "asr_model_02", nullable = true)
    private String asrModelId;

    @Schema(description = "VAD Model ID", example = "vad_model_02", nullable = true)
    private String vadModelId;

    @Schema(description = "LLM MOdel ID", example = "llm_model_02", nullable = true)
    private String llmModelId;

    @Schema(description = "VLLM Model ID", example = "vllm_model_02", required = false)
    private String vllmModelId;

    @Schema(description = "TTS Model ID", example = "tts_model_02", required = false)
    private String ttsModelId;

    @Schema(description = "Timbre ID", example = "voice_02", nullable = true)
    private String ttsVoiceId;

    @Schema(description = "Memory ID", example = "mem_model_02", nullable = true)
    private String memModelId;

    @Schema(description = "Intent Recognition ID", example = "intent_model_02", nullable = true)
    private String intentModelId;

    @Schema(description = "Plugin Function Info", nullable = true)
    private List<FunctionInfo> functions;   

    @Schema(description = "Role Setting Parameter", example = "You are a professional Customer Service Assistant.", nullable = true)
    private String systemPrompt;

    @Schema(description = "Summary memory", example = "Build a scalable dynamic memory network that retains key information within limited space while intelligently maintaining the evolution of information.\n" +
"Summarize important user information based on conversation history to provide more personalized services in future interactions.",  nullable = true)
    private String summaryMemory;

    @Schema(description = "Chat record configuration (0: no recording, 1: record text only, 2: record text and audio)", example = "3", nullable = true)
    private Integer chatHistoryConf;
    



    @Schema(description = "Language Code", example = "zh_CN", nullable = true)
    private String langCode;

    @Schema(description = "Interaction Language", example = "中文", nullable = true)
    private String language;

    @Schema(description = "Sort", example = "1", nullable = true)
    private Integer sort;

    @Data
    @Schema(description = "Plugin Function Info")
    public static class FunctionInfo implements Serializable {
        @Schema(description = "Plugin ID", example = "plugin_01")
        private String pluginId;

        @Schema(description = "Function Parameter Info", nullable = true)
        private HashMap<String, Object> paramInfo;

        private static final long serialVersionUID = 1L;
    }
}