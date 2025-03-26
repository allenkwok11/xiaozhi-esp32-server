package xiaozhi.modules.device.controller;

import cn.hutool.json.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.ObjectUtils;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.controller.BaseController;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.agent.domain.Agent;
import xiaozhi.modules.agent.service.AgentService;
import xiaozhi.modules.device.constant.DeviceConstant;
import xiaozhi.modules.device.domain.Device;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.device.vo.DeviceCodeVO;
import xiaozhi.modules.ota.domain.Ota;
import xiaozhi.modules.security.user.SecurityUser;

import java.util.Date;

@Slf4j
@Tag(name = "设备管理")
@AllArgsConstructor
@RestController
@RequestMapping("/user/agent/device")
public class UserDeviceController extends BaseController {
    private final AgentService agentService;
    private final DeviceService deviceService;
    private final RedisUtils redisUtils;

    @GetMapping("/bind/{agentId}")
    @Operation(summary = "已绑定设备列表")
    @RequiresPermissions("sys:role:normal")
    public Result<Page<Device>> bindDeviceList(@PathVariable String agentId, @RequestParam Integer pageNo, @RequestParam Integer pageSize) {
        if (StringUtils.isBlank(agentId)) {
            log.error("智能体ID不能为空");
            return new Result().error("智能体ID不能为空");
        }

        UserDetail user = SecurityUser.getUser();
        Agent agent = agentService.getById(agentId);
        if (ObjectUtils.isNull(agent)) {
            log.error("智能体不存在");
            return new Result().error("智能体不存在");
        }
        Page page = new Page<Device>(pageNo, pageSize);
        page = deviceService.page(page, new QueryWrapper<Device>().eq("user_id", user.getId()).eq("agent_id", agentId));
        return new Result<Page<Device>>().ok(page);
    }


    @PostMapping("/bind/{agentId}")
    @Operation(summary = "绑定设备")
    @RequiresPermissions("sys:role:normal")
    public Result<Device> bindDevice(@PathVariable String agentId, @RequestBody DeviceCodeVO deviceCodeVO) {
        if (ObjectUtils.isNull(deviceCodeVO) || StringUtils.isBlank(deviceCodeVO.getDeviceCode())) {
            log.error("授权码不能为空");
            return new Result().error("授权码不能为空");
        }
        if (StringUtils.isBlank(agentId)) {
            log.error("智能体ID不能为空");
            return new Result().error("智能体ID不能为空");
        }

        UserDetail user = SecurityUser.getUser();

        // 从 Redis 中获取设备信息
        Object redisValue = redisUtils.hGet(DeviceConstant.REDIS_KEY_PREFIX_DEVICE_ACTIVATION_CODE, deviceCodeVO.getDeviceCode());
        if (ObjectUtils.isNull(redisValue)) {
            log.error("授权码不存在:{}", deviceCodeVO.getDeviceCode());
            return new Result().error("授权码不存在");
        }
        JSONObject jsonObject = (JSONObject) redisValue;
        try {
            redisUtils.hDel(DeviceConstant.REDIS_KEY_PREFIX_DEVICE_ACTIVATION_CODE, deviceCodeVO.getDeviceCode());
            redisUtils.hDel(DeviceConstant.REDIS_KEY_PREFIX_DEVICE_ACTIVATION_MAC, jsonObject.getStr("mac_address").toUpperCase());
        } catch (Exception e) {
            log.warn("授权缓存删除失败", e);
        }
        JSONObject board = jsonObject.getJSONObject("board");
        JSONObject application = jsonObject.getJSONObject("application");
        if (ObjectUtils.isNull(board) || ObjectUtils.isNull(application)) {
            log.error("设备码绑定信息无效，{}:{}", jsonObject.getStr("mac_address").toUpperCase(), deviceCodeVO.getDeviceCode());
            return new Result().error("设备码绑定信息无效");
        }

        Agent agent = agentService.getById(agentId);
        if (ObjectUtils.isNull(agent)) {
            log.error("智能体不存在");
            return new Result().error("智能体不存在");
        }
        Device device = new Device();
        device.setId(jsonObject.getStr("uuid").replace("-", ""));
        device.setUserId(user.getId());
        device.setMacAddress(jsonObject.getStr("mac_address").toUpperCase());
        device.setBoard(board.getStr("type"));
        device.setAppVersion(application.getStr("version"));
        device.setAgentId(agentId);
        device.setCreator(user.getId());
        device.setCreateDate(new Date());
        device.setAutoUpdate(1);
        boolean bool = deviceService.save(device);
        if (!bool) {
            return new Result().error("绑定失败");
        }
        return new Result<Device>().ok(device);
    }

    @PutMapping("/unbind/{deviceId}")
    @Operation(summary = "解绑设备")
    @RequiresPermissions("sys:role:normal")
    public Result<Device> bindDevice(@PathVariable String deviceId) {
        if (StringUtils.isBlank(deviceId)) {
            log.error("设备ID不能为空");
            return new Result().error("设备ID不能为空");
        }
        boolean bool = deviceService.removeById(deviceId);
        if (!bool) {
            return new Result().error("解绑失败");
        }
        return new Result<Device>().ok(null);
    }

    @PostMapping("/autoUpdate/{deviceId}")
    @Operation(summary = "切换设备OTA升级状态")
    @RequiresPermissions("sys:role:normal")
    public Result<Device> toggleAutoUpdate(@PathVariable String deviceId, @RequestBody Device device) {
        if (StringUtils.isBlank(deviceId)) {
            log.error("设备ID不能为空");
            return new Result().error("设备ID不能为空");
        }
        UserDetail user = SecurityUser.getUser();
        boolean bool = deviceService.update(
                new UpdateWrapper<Device>().eq("id", deviceId)
                        .set("auto_update", device.getAutoUpdate())
                        .set("updater", user.getId())
                        .set("update_date", new Date())
        );
        if (!bool) {
            return new Result<Device>().error("切换设备OTA升级状态失败");
        }
        return new Result<Device>().ok(null);
    }

    @PostMapping("/alias/{deviceId}")
    @Operation(summary = "设置设备别名")
    @RequiresPermissions("sys:role:normal")
    public Result<Device> setAlias(@PathVariable String deviceId, @RequestBody Device device) {
        if (StringUtils.isBlank(deviceId)) {
            log.error("设备ID不能为空");
            return new Result().error("设备ID不能为空");
        }
        UserDetail user = SecurityUser.getUser();
        boolean bool = deviceService.update(
                new UpdateWrapper<Device>().eq("id", deviceId)
                        .set("alias", device.getAlias())
                        .set("updater", user.getId())
                        .set("update_date", new Date())
        );
        if (!bool) {
            return new Result<Device>().error("设置设备别名失败");
        }
        return new Result<Device>().ok(null);
    }
}