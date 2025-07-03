package xiaozhi.modules.sys.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Min;
import lombok.Data;

/**
 * 管理员分页用户的参数DTO
 * 
 * @author zjy
 * @since 2025-3-21
 */
@Data
@Schema(description = "DTO for admin paginated user parameters")
public class AdminPageUserDTO {

    @Schema(description = "Phone Number")
    private String mobile;

    @Schema(description = "Page")
    @Min(value = 0, message = "{sort.number}")
    private String page;

    @Schema(description = "Display columns")
    @Min(value = 0, message = "{sort.number}")
    private String limit;
}
