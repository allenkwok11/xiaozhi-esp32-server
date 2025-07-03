package xiaozhi.modules.device.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Getter;
import lombok.Setter;

/**
 * 设备注册头信息
 * 
 * @author zjy
 * @since 2025-3-28
 */
@Setter
@Getter
@Schema(description = "Device registration header information")
public class DeviceRegisterDTO implements Serializable {

    @Schema(description = "mac address")
    private String macAddress;

}