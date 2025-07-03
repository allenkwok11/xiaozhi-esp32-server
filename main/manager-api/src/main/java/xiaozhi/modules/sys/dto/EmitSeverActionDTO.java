package xiaozhi.modules.sys.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import xiaozhi.modules.sys.enums.ServerActionEnum;

/**
 * 发送python服务端操作DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class EmitSeverActionDTO
{
    @Schema(description = "target ws address")
    @NotEmpty(message = "target ws address cannot be empty")
    private String targetWs;

    @Schema(description = "designated operation")
    @NotNull(message = "operation cannot be empty")
    private ServerActionEnum action;
}
