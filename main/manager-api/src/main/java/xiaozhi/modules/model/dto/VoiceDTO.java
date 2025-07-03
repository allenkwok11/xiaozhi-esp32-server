package xiaozhi.modules.model.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Voice Info")
public class VoiceDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "Voice ID")
    private String id;

    @Schema(description = "Voice Name")
    private String name;
}