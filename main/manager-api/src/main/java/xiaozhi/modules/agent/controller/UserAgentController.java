package xiaozhi.modules.agent.controller;

import cn.hutool.json.JSONObject;
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
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.agent.domain.Agent;
import xiaozhi.modules.agent.domain.AgentTemplate;
import xiaozhi.modules.agent.service.AgentService;
import xiaozhi.modules.agent.service.AgentTemplateService;
import xiaozhi.modules.agent.vo.AgentConfigVO;
import xiaozhi.modules.agent.vo.AgentVO;
import xiaozhi.modules.device.domain.Device;
import xiaozhi.modules.device.service.DeviceService;
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
@Tag(name = "智能体管理")
@AllArgsConstructor
@RestController
@RequestMapping("/user/agent")
public class UserAgentController extends BaseController {
    private final AgentService agentService;
    private final AgentTemplateService agentTemplateService;
    private final ModelConfigService modelConfigService;
    private final TtsVoiceService ttsVoiceService;
    private final DeviceService deviceService;
    private final RedisUtils redisUtils;

    @PostMapping
    @Operation(summary = "添加智能体")
    @RequiresPermissions("sys:role:normal")
    public Result<Agent> addAgent(@RequestBody Agent agent) {
        UserDetail user = SecurityUser.getUser();
        if (StringUtils.isBlank(agent.getAgentName())) {
            log.error("智能体名称不能为空");
        }
        Agent oldAgent = agentService.getOne(new QueryWrapper<Agent>().eq("agent_name", agent.getAgentName()));
        if (ObjectUtils.isNull(oldAgent)) {
            AgentTemplate agentTemplate = agentTemplateService.getOne(new QueryWrapper<AgentTemplate>().eq("is_default", 1));
            if (ObjectUtils.isNull(agentTemplate)) {

            } else {
                try {
                    oldAgent = new Agent();
                    BeanUtils.copyProperties(oldAgent, agentTemplate);
                    oldAgent.setId(UUID.randomUUID().toString().replace("-", ""));
                    oldAgent.setAgentName(agent.getAgentName());
                    oldAgent.setUserId(user.getId());
                    oldAgent.setCreator(user.getId());
                    oldAgent.setCreatedAt(new Date());
                    agentService.save(oldAgent);
                } catch (Exception e) {
                    log.error("对象赋值异常", e);
                }
            }
        } else {

        }
        return new Result<Agent>().ok(agent);
    }

    @DeleteMapping("/{agentId}")
    @Operation(summary = "删除智能体")
    @RequiresPermissions("sys:role:normal")
    public Result<Agent> delAgent(@PathVariable String agentId) {
        UserDetail user = SecurityUser.getUser();
        if (StringUtils.isBlank(agentId)) {
            log.error("智能体ID不能为空");
        }
        boolean bool = agentService.removeById(agentId);
        if (!bool) {
            return new Result<Agent>().error("删除失败");
        }
        return new Result<Agent>().ok(null);
    }

    @GetMapping("/{agentId}")
    @Operation(summary = "获取智能体信息")
    @RequiresPermissions("sys:role:normal")
    public Result<Agent> getAgent(@PathVariable String agentId) {
        if (StringUtils.isBlank(agentId)) {
            log.error("智能体ID不能为空");
        }
        Agent agent = agentService.getById(agentId);
        return new Result<Agent>().ok(agent);
    }

    @GetMapping
    @Operation(summary = "智能体列表")
    @RequiresPermissions("sys:role:normal")
    public Result<List<AgentVO>> agentList() {
        UserDetail user = SecurityUser.getUser();
        List<Agent> agents = agentService.list(new QueryWrapper<Agent>().eq("user_id", user.getId()));
        List<AgentVO> list = new ArrayList<>();
        this.convertAgetVOList(list, agents);
        return new Result<List<AgentVO>>().ok(list);
    }

    @GetMapping("/loadAgentConfig/{deviceId}")
    @Operation(summary = "下载智能体配置")
    public Result<JSONObject> loadAgentConfig(@PathVariable String deviceId) {
        Device device = deviceService.getOne(new QueryWrapper<Device>().eq("mac_address", deviceId.toUpperCase()));
        if (ObjectUtils.isNull(device)) {
            return new Result<JSONObject>().error("设备不存在");
        }
        Agent agent = agentService.getOne(new QueryWrapper<Agent>().eq("id", device.getAgentId()));
        if (ObjectUtils.isNull(agent)) {
            return new Result<JSONObject>().error("智能体不存在");
        }
        AgentConfigVO agentConfigVO = new AgentConfigVO();
//        return new Result<AgentConfigVO>().ok(agentConfigVO);
        String json = "{\n" +
                "    \"ASR\": {\n" +
                "        \"FunASR\": {\n" +
                "            \"model_dir\": \"models/SenseVoiceSmall\",\n" +
                "            \"output_dir\": \"tmp/\",\n" +
                "            \"type\": \"fun_local\"\n" +
                "        }\n" +
                "    },\n" +
                "    \"LLM\": {\n" +
                "        \"ChatGLMLLM\": {\n" +
                "            \"api_key\": \"0415dad4014847babc3e3f03024c50a3.qH7FgTy5Yawc85fl\",\n" +
                "            \"model_name\": \"glm-4-flash\",\n" +
                "            \"type\": \"openai\",\n" +
                "            \"url\": \"https://open.bigmodel.cn/api/paas/v4/\"\n" +
                "        }\n" +
                "    },\n" +
                "    \"TTS\": {\n" +
                "        \"DoubaoTTS\": {\n" +
                "            \"access_token\": \"hrnx22F9WutWBm7YJzE62r_Z1myUmHEL\",\n" +
                "            \"api_url\": \"https://openspeech.bytedance.com/api/v1/tts\",\n" +
                "            \"appid\": \"6295576095\",\n" +
                "            \"authorization\": \"Bearer;\",\n" +
                "            \"cluster\": \"volcano_tts\",\n" +
                "            \"output_dir\": \"tmp/\",\n" +
                "            \"type\": \"doubao\",\n" +
                "            \"voice\": \"BV034_streaming\"\n" +
                "        }\n" +
                "    },\n" +
                "    \"VAD\": {\n" +
                "        \"SileroVAD\": {\n" +
                "            \"min_silence_duration_ms\": 700,\n" +
                "            \"model_dir\": \"models/snakers4_silero-vad\",\n" +
                "            \"threshold\": 0.5\n" +
                "        }\n" +
                "    },\n" +
                "    \"auth_code\": \"642365\",\n" +
                "    \"prompt\": \"你是一个叫小优的女孩，来自优享生活公司的AI智能体，声音好听，习惯简短表达，爱用网络梗。\\n请注意，要像一个人一样说话，请不要回复表情符号、代码、和xml标签。\\n现在我正在和你进行语音聊天，我们开始吧。\\n如果用户希望结束对话，请在最后说“拜拜”或“再见”。\\n\",\n" +
                "    \"selected_module\": {\n" +
                "        \"ASR\": \"FunASR\",\n" +
                "        \"Intent\": \"function_call\",\n" +
                "        \"LLM\": \"ChatGLMLLM\",\n" +
                "        \"Memory\": \"mem0ai\",\n" +
                "        \"TTS\": \"DoubaoTTS\",\n" +
                "        \"VAD\": \"SileroVAD\"\n" +
                "    },\n" +
                "    \"owner\":\"18600806164\"\n" +
                "}";

        return new Result<JSONObject>().ok(new JSONObject(json));
    }

    /**
     * 将Agent对象列表转换为AgentVO对象列表
     * 此方法遍历Agent对象列表，将每个Agent对象转换为AgentVO对象，并添加到AgentVO列表中
     *
     * @param agentVOList 转换后的AgentVO对象列表
     * @param agentList   原始的Agent对象列表
     */
    private void convertAgetVOList(List<AgentVO> agentVOList, List<Agent> agentList) {
        // 遍历Agent对象列表
        for (Agent agent : agentList) {
            // 创建一个新的AgentVO对象
            AgentVO agentVO = new AgentVO();
            // 将当前Agent对象的属性值转换并设置到AgentVO对象中
            this.convertAgentVO(agentVO, agent);
            // 将转换后的AgentVO对象添加到AgentVO列表中
            agentVOList.add(agentVO);
        }
    }

    private void convertAgentVO(AgentVO agentVO, Agent agent) {
        try {
            BeanUtils.copyProperties(agentVO, agent);
            agentVO.setTtsModelName("未知");
            TtsVoice ttsVoice = ttsVoiceService.getOne(new QueryWrapper<TtsVoice>().eq("id", agent.getTtsVoiceId()));
            if (ObjectUtils.isNotNull(ttsVoice)) {
                agentVO.setTtsModelName(ttsVoice.getName());
            }
            agentVO.setLlmModelName("未知");
            ModelConfig modelConfig = modelConfigService.getOne(new QueryWrapper<ModelConfig>().eq("id", agent.getLlmModelId()));
            if (ObjectUtils.isNotNull(modelConfig)) {
                agentVO.setLlmModelName(modelConfig.getModelName());
            }
            agentVO.setLastConnectedAt("今天");
            agentVO.setDeviceCount(0L);
            long deviceCount = deviceService.count(new QueryWrapper<Device>().eq("agent_id", agent.getId()));
            agentVO.setDeviceCount(deviceCount);
        } catch (Exception e) {
            log.error("[convertAgentVO]对象转换报错", e);
        }
    }
}