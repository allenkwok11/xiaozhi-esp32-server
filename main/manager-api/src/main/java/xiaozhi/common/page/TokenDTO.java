package xiaozhi.common.page;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 令牌信息
 *
 * @author Jack
 */
@Data
@Schema(description = "Token Info")
public class TokenDTO implements Serializable {

    @Schema(description = "Password")
    private String token;

    @Schema(description = "Expired Date")
    private int expire;

    @Schema(description = "Client Fingerprint")
    private String clientHash;
}
