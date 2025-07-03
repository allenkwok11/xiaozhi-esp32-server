package xiaozhi.modules.device.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "User device list display VO")
public class UserShowDeviceListVO {

    @Schema(description = "App version")
    private String appVersion;

    @Schema(description = "Bound user name")
    private String bindUserName;

    @Schema(description = "Device model")
    private String deviceType;

    @Schema(description = "Device unique identifier")
    private String id;

    @Schema(description = "MAC address")
    private String macAddress;

    @Schema(description = "OTA enabled")
    private Integer otaUpgrade;

    @Schema(description = "last chat time")
    private String recentChatTime;

}