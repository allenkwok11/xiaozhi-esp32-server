package xiaozhi.modules.agent.mapper;

import org.apache.ibatis.annotations.Mapper;
import xiaozhi.modules.agent.domain.Agent;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
* @author chenerlei
* @description 针对表【ai_agent(智能体配置表)】的数据库操作Mapper
* @createDate 2025-03-22 11:48:18
* @Entity xiaozhi.modules.agent.domain.Agent
*/
@Mapper
public interface AgentMapper extends BaseMapper<Agent> {

}




