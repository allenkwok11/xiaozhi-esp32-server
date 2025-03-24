package xiaozhi.modules.agent.vo;

import lombok.Data;
import xiaozhi.modules.agent.domain.Agent;

@Data
public class AgentVO extends Agent {
    //角色音色
    private String ttsModelName;

    //角色明星
    private String llmModelName;

    //最近对话
    private String lastConnectedAt;

    //设备数量
    private Long deviceCount;
}
