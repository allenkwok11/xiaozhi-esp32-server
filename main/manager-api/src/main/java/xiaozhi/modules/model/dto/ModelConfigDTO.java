package xiaozhi.modules.model.dto;

import java.io.Serial;
import java.io.Serializable;

import cn.hutool.json.JSONObject;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "Model provider")
public class ModelConfigDTO implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    @Schema(description = "Primary key")
    private String id;

    @Schema(description = "Model type(Memory/ASR/VAD/LLM/TTS)")
    private String modelType;

    @Schema(description = "Model code(e.g., AliLLM、DoubaoTTS)")
    private String modelCode;

    @Schema(description = "Model name")
    private String modelName;

    @Schema(description = "default config status(0: no 1: yes)")
    private Integer isDefault;

    @Schema(description = "enabled status")
    private Integer isEnabled;

    @Schema(description = "Model Config (JSON format)")
    private JSONObject configJson;

    @Schema(description = "Official documentation link")
    private String docLink;

    @Schema(description = "Remarks")
    private String remark;

    @Schema(description = "Sort order")
    private Integer sort;
}
