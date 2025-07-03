package xiaozhi.modules.device.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Data
@Schema(description = "Device OTA version check response body, including activation code requirement")
public class DeviceReportRespDTO {
    @Schema(description = "Server time")
    private ServerTime server_time;

    @Schema(description = "Activation code")
    private Activation activation;

    @Schema(description = "error message")
    private String error;

    @Schema(description = "Firmware version info")
    private Firmware firmware;
    
    @Schema(description = "WebSocket config")
    private Websocket websocket;

    @Getter
    @Setter
    public static class Firmware {
        @Schema(description = "version")
        private String version;
        @Schema(description = "download url")
        private String url;
    }

    public static DeviceReportRespDTO createError(String message) {
        DeviceReportRespDTO resp = new DeviceReportRespDTO();
        resp.setError(message);
        return resp;
    }

    @Setter
    @Getter
    public static class Activation {
        @Schema(description = "Activation code")
        private String code;

        @Schema(description = "Activation code info: activation URL")
        private String message;

        @Schema(description = "Challenge code")
        private String challenge;
    }

    @Getter
    @Setter
    public static class ServerTime {
        @Schema(description = "Timestamp")
        private Long timestamp;

        @Schema(description = "Time Zone")
        private String timeZone;

        @Schema(description = "Time zone offset in minutes")
        private Integer timezone_offset;
    }
    
    @Getter
    @Setter
    public static class Websocket {
        @Schema(description = "WebSocket server address")
        private String url;
    }
}
