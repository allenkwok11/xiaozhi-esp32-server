package xiaozhi.modules.agent.service.biz.impl;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import xiaozhi.modules.agent.dto.AgentChatHistoryReportDTO;
import xiaozhi.modules.agent.entity.AgentEntity;
import xiaozhi.modules.agent.entity.AgentChatHistoryEntity;
import xiaozhi.modules.agent.service.AgentChatHistoryService;
import xiaozhi.modules.agent.service.AgentService;
import xiaozhi.modules.agent.service.biz.AgentChatHistoryBizService;

import javax.annotation.Nullable;

/**
 * {@link AgentChatHistoryBizService} impl
 *
 * @author Goody
 * @version 1.0, 2025/4/30
 * @since 1.0.0
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class AgentChatHistoryBizServiceImpl implements AgentChatHistoryBizService {
    private final AgentService agentService;
    private final AgentChatHistoryService agentChatHistoryService;

    /**
     * 处理聊天记录上报，包括文件上传和相关信息记录
     *
     * @param report 包含聊天上报所需信息的输入对象
     * @return 上传结果，true表示成功，false表示失败
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public Boolean report(AgentChatHistoryReportDTO report) {
        final String macAddress = report.getMacAddress();
        final Byte chatType = report.getChatType();
        log.info("小智设备聊天上报请求: macAddress={}, type={}", macAddress, chatType);

        // 1. 上传音频文件
        final String uploadUrl = this.upload(report);

        // 2. 组装上报数据
        // 2.1 根据设备MAC地址查询对应的默认智能体，判断是否需要上报
        AgentEntity agentEntity = agentService.getDefaultAgentByMacAddress(macAddress);
        if (agentEntity == null) {
            return false;
        }
        final String agentId = agentEntity.getId();
        log.info("设备 {} 对应智能体 {} 上报", macAddress, agentEntity.getId());

        // 2.2 构建聊天记录实体
        final AgentChatHistoryEntity entity = AgentChatHistoryEntity.builder()
                .macAddress(macAddress)
                .agentId(agentId)
                .sessionId(report.getSessionId())
                .sort(report.getSort())
                .chatType(report.getChatType())
                .content(report.getContent())
                .audio(report.getFileBase64())
                .audioUrl(uploadUrl)
                .build();

        // 3. 保存数据
        agentChatHistoryService.save(entity);
        return Boolean.TRUE;
    }

    /**
     * 上传文件
     *
     * @param report 上报文件数据
     * @return 上传文件url
     */
    @Nullable
    private String upload(AgentChatHistoryReportDTO report) {
        // TODO(haotian): 2025/4/30 根据需要自定义完成上传生成url即可
        return null;
    }
}
