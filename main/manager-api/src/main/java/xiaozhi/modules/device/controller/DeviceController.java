package xiaozhi.modules.device.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.device.dto.DeviceBindDTO;
import xiaozhi.modules.device.dto.DeviceUnBindDTO;
import xiaozhi.modules.device.entity.DeviceEntity;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.security.user.SecurityUser;

import java.util.List;

@Tag(name = "设备管理")
@AllArgsConstructor
@RestController
@RequestMapping("/device")
public class DeviceController {
    private final DeviceService deviceService;

    private final RedisUtils redisUtils;


    @PostMapping("/bind/{agentId}")
    @Operation(summary = "绑定设备")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> bindDevice(@PathVariable String agentId,@RequestBody String code) {
        String macAddress = (String) redisUtils.get(RedisKeys.getDeviceCaptchaKey(code));
        if (StringUtils.isBlank(macAddress)) {
            return new Result<Void>().error(ErrorCode.DEVICE_CAPTCHA_ERROR);
        }
        Long user = SecurityUser.getUser().getId();
        DeviceBindDTO deviceBindDTO = new DeviceBindDTO(macAddress,user,agentId);
        deviceService.bindDevice(deviceBindDTO);
        return new Result<>();
    }

    @GetMapping("/bind")
    @Operation(summary = "获取已绑定设备")
    @RequiresPermissions("sys:role:normal")
    public Result<List<DeviceEntity>> getUserDevices() {
        UserDetail user = SecurityUser.getUser();
        List<DeviceEntity> devices = deviceService.getUserDevices(user.getId());
        return new Result<List<DeviceEntity>>().ok(devices);
    }

    @PostMapping("/unbind")
    @Operation(summary = "解绑设备")
    @RequiresPermissions("sys:role:normal")
    public Result unbindDevice(@RequestBody DeviceUnBindDTO unDeviveBind) {
        UserDetail user = SecurityUser.getUser();
        deviceService.unbindDevice(user.getId(), unDeviveBind.getDeviceId());
        return new Result();
    }


}