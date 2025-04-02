package xiaozhi.modules.device.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 查询所有设备的DTO
 * 
 * @author zjy
 * @since 2025-3-21
 */
@Data
@Schema(description = "查询所有设备的DTO")
public class DevicePageUserDTO {

    @Schema(description = "设备关键词")
    private String keywords;

    @Schema(description = "页数")
    private String page;

    @Schema(description = "显示列数")
    private String limit;
}
