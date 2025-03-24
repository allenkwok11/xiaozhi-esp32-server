package xiaozhi.modules.agent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import xiaozhi.modules.agent.domain.Agent;
import xiaozhi.modules.agent.service.AgentService;
import xiaozhi.modules.agent.mapper.AgentMapper;
import org.springframework.stereotype.Service;

/**
* @author chenerlei
* @description 针对表【ai_agent(智能体配置表)】的数据库操作Service实现
* @createDate 2025-03-22 11:48:18
*/
@Service
public class AgentServiceImpl extends ServiceImpl<AgentMapper, Agent>
    implements AgentService{

}




