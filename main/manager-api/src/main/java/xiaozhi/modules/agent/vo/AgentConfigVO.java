package xiaozhi.modules.agent.vo;

import cn.hutool.json.JSONObject;
import lombok.Data;

@Data
public class AgentConfigVO {
    private JSONObject selected_module;
    private String prompt;
    private JSONObject LLM;
    private JSONObject TTS;
    private JSONObject ASR;
    private JSONObject VAD;
    private JSONObject Memory;
    private JSONObject Intent;
    private String owner;
}
