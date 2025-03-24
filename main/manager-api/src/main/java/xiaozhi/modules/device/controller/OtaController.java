package xiaozhi.modules.device.controller;

import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.ObjectUtils;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.HttpHeaders;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.controller.BaseController;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.modules.device.constant.DeviceConstant;
import xiaozhi.modules.device.domain.Device;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.device.utils.CodeGeneratorUtil;
import xiaozhi.modules.device.vo.DeviceOtaVO;
import xiaozhi.modules.sys.service.SysParamsService;

import java.util.Date;

@Slf4j
@Tag(name = "设备OTA管理")
@AllArgsConstructor
@RestController
@RequestMapping("/ota")
public class OtaController extends BaseController {
    private final DeviceService deviceService;
    private final SysParamsService sysParamsService;
    @Resource
    private RedisUtils redisUtils;
    private final String OTA_PARAM_CODE = "OTA";

    @CrossOrigin(originPatterns = "*", methods = {RequestMethod.GET, RequestMethod.POST})
    @RequestMapping(path = "/", method = {RequestMethod.POST, RequestMethod.GET}, produces = "application/json")
    @Operation(summary = "设备OTA升级")
    public String ota(@RequestHeader(required = false) HttpHeaders headers, @RequestBody(required = false) JSONObject jsonObject) {
        log.info("OTA升级请求：header:{}，body:{}", headers, jsonObject);
        if (ObjectUtils.isNull(headers) || StringUtils.isBlank(headers.getFirst("device-id"))) {
            log.error("设备ID不能为空");
            return "{\"error\": \"Device ID is required\"}";
        }

        DeviceOtaVO otaVO = new DeviceOtaVO();
        Device device = deviceService.getOne(new UpdateWrapper<Device>().eq("mac_address", headers.getFirst("device-id").toUpperCase()).eq("id", headers.getFirst("client-Id").replace("-", "")));
        if (ObjectUtils.isNull(device)) {
            // 从 Redis 中获取设备信息
            Object redisValue = redisUtils.hGet(DeviceConstant.REDIS_KEY_PREFIX_DEVICE_ACTIVATION_MAC, headers.getFirst("device-id").toUpperCase());
            if (ObjectUtils.isNull(redisValue)) {
                String code = CodeGeneratorUtil.generateCode(6);
                log.info("[gen]授权码已广播:{}", code);
                otaVO.setActivation(new DeviceOtaVO.Activation(code, "youxlife.com\n" + code));
                redisUtils.hSet(DeviceConstant.REDIS_KEY_PREFIX_DEVICE_ACTIVATION_MAC, headers.getFirst("device-id").toUpperCase(), code, RedisUtils.HOUR_ONE_EXPIRE);
                redisUtils.hSet(DeviceConstant.REDIS_KEY_PREFIX_DEVICE_ACTIVATION_CODE, code, jsonObject, RedisUtils.HOUR_ONE_EXPIRE);
            } else {
                log.warn("[get]授权码已广播:{}", redisValue);
                otaVO.setActivation(new DeviceOtaVO.Activation(redisValue.toString(), "youxlife.com\n" + redisValue));
            }
        }


        if (ObjectUtils.isNull(device) || device.getAutoUpdate() == 1) {
            //{"version":"1.0.0","url":"http://https://youxlife.oss-cn-zhangjiakou.aliyuncs.com/v1.4.5.bin"}
            String value = sysParamsService.getValue(OTA_PARAM_CODE);
            if (StringUtils.isBlank(value)) {
                log.warn("OTA升级信息未配置");
            } else {
                JSONObject object = new JSONObject(value);
                otaVO.setFirmware(new DeviceOtaVO.Firmware(object.getStr("version"), object.getStr("url")));
            }
        }

        otaVO.setServer_time(new DeviceOtaVO.ServerTime(new Date().getTime(), 8 * 60));
        return JSONUtil.toJsonStr(otaVO);
    }
}