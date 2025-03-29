package xiaozhi.modules.agent.vo;

import lombok.Data;
import xiaozhi.modules.agent.domain.Agent;
import xiaozhi.modules.agent.domain.AgentTemplate;

@Data
public class AgentTemplateVO extends AgentTemplate {
    //角色音色
    private String ttsModelName;

    //角色模型
    private String llmModelName;
}
