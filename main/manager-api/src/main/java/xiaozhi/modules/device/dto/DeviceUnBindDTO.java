package xiaozhi.modules.device.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 设备解绑表单
 */
@Data
@Schema(description = "device unbind table")
public class DeviceUnBindDTO implements Serializable {

    @Schema(description = "device ID")
    @NotBlank(message = "device ID cannot be null")
    private String deviceId;

}