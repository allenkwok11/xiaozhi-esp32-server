package xiaozhi.modules.sys.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 修改密码
 */
@Data
@Schema(description = "edit password")
public class PasswordDTO implements Serializable {

    @Schema(description = "original password")
    @NotBlank(message = "{sysuser.password.require}")
    private String password;

    @Schema(description = "new password")
    @NotBlank(message = "{sysuser.password.require}")
    private String newPassword;

}