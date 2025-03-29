package xiaozhi.modules.agent.vo;

import lombok.Data;
import xiaozhi.modules.agent.entity.AgentTemplateEntity;

@Data
public class AgentTemplateVO extends AgentTemplateEntity {
    // 角色音色
    private String ttsModelName;

    // 角色模型
    private String llmModelName;
}
