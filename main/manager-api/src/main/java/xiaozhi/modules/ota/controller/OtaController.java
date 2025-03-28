package xiaozhi.modules.ota.controller;

import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.ObjectUtils;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.http.HttpHeaders;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.controller.BaseController;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.device.constant.DeviceConstant;
import xiaozhi.modules.device.domain.Device;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.device.utils.CodeGeneratorUtil;
import xiaozhi.modules.device.vo.DeviceOtaVO;
import xiaozhi.modules.ota.domain.Ota;
import xiaozhi.modules.ota.service.OtaService;
import xiaozhi.modules.security.user.SecurityUser;

import java.util.Date;

@Slf4j
@Tag(name = "设备OTA管理")
@AllArgsConstructor
@RestController
@RequestMapping("/ota")
public class OtaController extends BaseController {
    private final DeviceService deviceService;
    private final OtaService otaService;
    @Resource
    private RedisUtils redisUtils;

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
        Device device = deviceService.getOne(new UpdateWrapper<Device>().eq("mac_address", headers.getFirst("device-id").toUpperCase()).eq("id", headers.getFirst("client-Id").replace("-", "")), false);
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

        //规范输出，赋值默认数据
        otaVO.setFirmware(new DeviceOtaVO.Firmware("0.0.1", ""));
        if (ObjectUtils.isNull(device) || device.getAutoUpdate() == 1) {
            //{"version":"1.0.0","url":"http://https://youxlife.oss-cn-zhangjiakou.aliyuncs.com/v1.4.5.bin"}
            String board = ObjectUtils.isNull(device) ? headers.getFirst("user-agent").split("/")[0] : device.getBoard();
            Ota ota = otaService.getOne(new UpdateWrapper<Ota>().eq("board", board).eq("is_enabled", 1));
            if (ObjectUtils.isNotNull(ota)) {
                otaVO.setFirmware(new DeviceOtaVO.Firmware(ota.getAppVersion(), ota.getUrl()));
            }
        }

        otaVO.setServer_time(new DeviceOtaVO.ServerTime(new Date().getTime(), 8 * 60));
        return JSONUtil.toJsonStr(otaVO);
    }

    @GetMapping("/sys/getOtalist")
    @Operation(summary = "设备OTA列表")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Page<Ota>> getOtalist(@RequestParam Integer pageNo, @RequestParam Integer pageSize) {
        UserDetail user = SecurityUser.getUser();
        Page page = new Page<Ota>(pageNo, pageSize);
        page = otaService.page(page);
        return new Result<Page<Ota>>().ok(page);
    }

    @PostMapping("/sys/save")
    @Operation(summary = "添加设备OTA")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Ota> save(@RequestBody Ota ota) {
        UserDetail user = SecurityUser.getUser();
        ota.setCreator(user.getId());
        ota.setCreateDate(new Date());
        boolean bool = otaService.save(ota);
        if (!bool) {
            return new Result().error("设备OTA添加失败");
        }
        return new Result<Ota>().ok(null);
    }

    @PostMapping("/sys/update")
    @Operation(summary = "更新设备OTA")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Ota> update(@RequestBody Ota ota) {
        UserDetail user = SecurityUser.getUser();
        boolean bool = otaService.update(
                new UpdateWrapper<Ota>().eq("id", ota.getId())
                        .set("board", ota.getBoard().trim().toLowerCase())
                        .set("app_version", ota.getAppVersion())
                        .set("url", ota.getUrl())
                        .set("is_enabled", ota.getIsEnabled())
                        .set("updater", user.getId())
                        .set("update_date", new Date())
        );
        if (!bool) {
            return new Result().error("设备OTA更新失败");
        }
        return new Result<Ota>().ok(null);
    }

    @PostMapping("/sys/toggleEnabled")
    @Operation(summary = "切换设备OTA可用状态")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Ota> toggleEnabled(@RequestBody Ota ota) {
        UserDetail user = SecurityUser.getUser();
        boolean bool = otaService.update(
                new UpdateWrapper<Ota>().eq("id", ota.getId())
                        .set("is_enabled", ota.getIsEnabled())
                        .set("updater", user.getId())
                        .set("update_date", new Date())
        );
        if (!bool) {
            return new Result().error("切换设备OTA可用状态失败");
        }
        return new Result<Ota>().ok(null);
    }
}