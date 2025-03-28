package xiaozhi.modules.agent.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.ObjectUtils;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.controller.BaseController;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.agent.domain.AgentTemplate;
import xiaozhi.modules.agent.service.AgentTemplateService;
import xiaozhi.modules.agent.vo.AgentTemplateVO;
import xiaozhi.modules.model.domain.ModelConfig;
import xiaozhi.modules.model.domain.TtsVoice;
import xiaozhi.modules.model.service.ModelConfigService;
import xiaozhi.modules.model.service.TtsVoiceService;
import xiaozhi.modules.security.user.SecurityUser;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.UUID;

@Slf4j
@Tag(name = "智能体模板管理")
@AllArgsConstructor
@RestController
@RequestMapping("/user/agent/template")
public class AgentTemplateController extends BaseController {
    private final AgentTemplateService agentTemplateService;
    private final ModelConfigService modelConfigService;
    private final TtsVoiceService ttsVoiceService;

    @PostMapping
    @Operation(summary = "添加智能体模板")
    @RequiresPermissions("sys:role:normal")
    public Result<AgentTemplate> addTemplate(@RequestBody AgentTemplate agentTemplate) {
        UserDetail user = SecurityUser.getUser();
        if (StringUtils.isBlank(agentTemplate.getAgentName())) {
            log.error("智能体模板名称不能为空");
        }
        try {
            agentTemplate = new AgentTemplate();
            agentTemplate.setId(UUID.randomUUID().toString().replace("-", ""));
            agentTemplate.setAgentName(agentTemplate.getAgentName());
            agentTemplate.setCreator(user.getId());
            agentTemplate.setCreatedAt(new Date());
            agentTemplateService.save(agentTemplate);
        } catch (Exception e) {
            log.error("对象赋值异常", e);
        }
        return new Result<AgentTemplate>().ok(agentTemplate);
    }

    @DeleteMapping("/{templateId}")
    @Operation(summary = "删除智能体模板")
    @RequiresPermissions("sys:role:normal")
    public Result<AgentTemplate> delTemplate(@PathVariable String templateId) {
        UserDetail user = SecurityUser.getUser();
        if (StringUtils.isBlank(templateId)) {
            log.error("智能体模板ID不能为空");
        }
        boolean bool = agentTemplateService.removeById(templateId);
        if (!bool) {
            return new Result<AgentTemplate>().error("删除失败");
        }
        return new Result<AgentTemplate>().ok(null);
    }

    @GetMapping
    @Operation(summary = "智能体模板模板列表")
    @RequiresPermissions("sys:role:normal")
    public Result<List<AgentTemplate>> templateList() {
        List<AgentTemplate> list = agentTemplateService.list(new QueryWrapper<AgentTemplate>().orderByAsc("sort"));
        return new Result<List<AgentTemplate>>().ok(list);
    }

    @GetMapping("/vo")
    @Operation(summary = "智能体模板模板列表")
    @RequiresPermissions("sys:role:normal")
    public Result<List<AgentTemplateVO>> templateVOList() {
        UserDetail user = SecurityUser.getUser();
        List<AgentTemplate> templates = agentTemplateService.list();
        List<AgentTemplateVO> list = new ArrayList<>();
        this.convertAgentTemplateVOList(list, templates);
        return new Result<List<AgentTemplateVO>>().ok(list);
    }

    /**
     * 将Agent对象列表转换为AgentTemplateVO对象列表
     * 此方法遍历Agent对象列表，将每个Agent对象转换为AgentTemplateVO对象，并添加到AgentTemplateVO列表中
     *
     * @param agentVOList 转换后的AgentTemplateVO对象列表
     * @param agentList   原始的Agent对象列表
     */
    private void convertAgentTemplateVOList(List<AgentTemplateVO> agentVOList, List<AgentTemplate> agentList) {
        // 遍历Agent对象列表
        for (AgentTemplate agentTemplate : agentList) {
            // 创建一个新的AgentTemplateVO对象
            AgentTemplateVO agentTemplateVO = new AgentTemplateVO();
            // 将当前Agent对象的属性值转换并设置到AgentTemplateVO对象中
            this.convertAgentTemplateVO(agentTemplateVO, agentTemplate);
            // 将转换后的AgentTemplateVO对象添加到AgentTemplateVO列表中
            agentVOList.add(agentTemplateVO);
        }
    }

    private void convertAgentTemplateVO(AgentTemplateVO agentTemplateVO, AgentTemplate agentTemplate) {
        try {
            BeanUtils.copyProperties(agentTemplateVO, agentTemplate);
            agentTemplateVO.setTtsModelName("未知");
            TtsVoice ttsVoice = ttsVoiceService.getOne(new QueryWrapper<TtsVoice>().eq("id", agentTemplate.getTtsVoiceId()));
            if (ObjectUtils.isNotNull(ttsVoice)) {
                agentTemplateVO.setTtsModelName(ttsVoice.getName());
            }
            agentTemplateVO.setLlmModelName("未知");
            ModelConfig modelConfig = modelConfigService.getOne(new QueryWrapper<ModelConfig>().eq("id", agentTemplate.getLlmModelId()));
            if (ObjectUtils.isNotNull(modelConfig)) {
                agentTemplateVO.setLlmModelName(modelConfig.getModelName());
            }
        } catch (Exception e) {
            log.error("[convertAgentTemplateVO]对象转换报错", e);
        }
    }
}