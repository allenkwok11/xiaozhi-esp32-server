package xiaozhi.modules.device.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Min;
import lombok.Data;

/**
 * 查询所有设备的DTO
 * 
 * @author zjy
 * @since 2025-3-21
 */
@Data
@Schema(description = "searc for DTO of all device")
public class DevicePageUserDTO {

    @Schema(description = "device keywords")
    private String keywords;

    @Schema(description = "page")
    @Min(value = 0, message = "{page.number}")
    private String page;

    @Schema(description = "Display column counts")
    @Min(value = 0, message = "{limit.number}")
    private String limit;
}
