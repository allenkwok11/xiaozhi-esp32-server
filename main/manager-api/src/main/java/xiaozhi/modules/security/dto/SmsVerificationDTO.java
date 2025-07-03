package xiaozhi.modules.security.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 短信验证码请求DTO
 */
@Data
@Schema(description = "SMS verification code request")
public class SmsVerificationDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "Phone number")
    @NotBlank(message = "{sysuser.username.require}")
    private String phone;

    @Schema(description = "Verification Code")
    @NotBlank(message = "{sysuser.captcha.require}")
    private String captcha;

    @Schema(description = "Unique identifier")
    @NotBlank(message = "{sysuser.uuid.require}")
    private String captchaId;
}