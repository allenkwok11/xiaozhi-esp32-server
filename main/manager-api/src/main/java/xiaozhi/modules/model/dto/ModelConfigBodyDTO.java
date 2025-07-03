package xiaozhi.modules.model.dto;

import java.io.Serial;

import cn.hutool.json.JSONObject;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "Model Provider")
public class ModelConfigBodyDTO {

    @Serial
    private static final long serialVersionUID = 1L;

    // @Schema(description = "模型类型(Memory/ASR/VAD/LLM/TTS)")
    // private String modelType;
    //
    @Schema(description = "Model Code (e.g., AliLLM、DoubaoTTS)")
    private String modelCode;

    @Schema(description = "Model Name")
    private String modelName;

    @Schema(description = "default config status(0:no 1:yes)")
    private Integer isDefault;

    @Schema(description = "enable status")
    private Integer isEnabled;

    @Schema(description = "model config (JSON format)")
    private JSONObject configJson;

    @Schema(description = "official doc url")
    private String docLink;

    @Schema(description = "Remarks")
    private String remark;

    @Schema(description = "sort order")
    private Integer sort;
}
