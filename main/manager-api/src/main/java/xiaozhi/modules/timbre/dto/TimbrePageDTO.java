package xiaozhi.modules.timbre.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 音色分页参数DTO
 * 
 * @author zjy
 * @since 2025-3-21
 */
@Data
@Schema(description = "Timbre paginated parameters")
public class TimbrePageDTO {

    @Schema(description = "Associated TTS model primary key")
    @NotBlank(message = "{timbre.ttsModelId.require}")
    private String ttsModelId;

    @Schema(description = "Timbre name")
    private String name;

    @Schema(description = "page")
    private String page;

    @Schema(description = "display columns")
    private String limit;
}
