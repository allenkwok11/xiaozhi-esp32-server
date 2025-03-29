package xiaozhi.modules.agent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import xiaozhi.modules.agent.domain.AgentTemplate;
import xiaozhi.modules.agent.service.AgentTemplateService;
import xiaozhi.modules.agent.mapper.AgentTemplateMapper;
import org.springframework.stereotype.Service;

/**
* @author chenerlei
* @description 针对表【ai_agent_template(智能体配置模板表)】的数据库操作Service实现
* @createDate 2025-03-22 11:48:18
*/
@Service
public class AgentTemplateServiceImpl extends ServiceImpl<AgentTemplateMapper, AgentTemplate>
    implements AgentTemplateService{

}




