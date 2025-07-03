package xiaozhi.modules.sys.vo;

import java.util.Date;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 管理员分页展示用户的VO
 * @ zjy
 * 
 * @since 2025-3-25
 */
@Data
public class AdminPageUserVO {

    @Schema(description = "Device Counts")
    private String deviceCount;

    @Schema(description = "Phone Number")
    private String mobile;

    @Schema(description = "Status")
    private Integer status;

    @Schema(description = "User ID")
    private String userid;

    @Schema(description = "Registered date")
    private Date createDate;
}
