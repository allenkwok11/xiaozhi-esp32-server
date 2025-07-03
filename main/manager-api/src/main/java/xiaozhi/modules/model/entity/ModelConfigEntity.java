package xiaozhi.modules.model.entity;

import java.util.Date;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;

import cn.hutool.json.JSONObject;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@TableName(value = "ai_model_config", autoResultMap = true)
@Schema(description = "Model Config Table")
public class ModelConfigEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "Primary key")
    private String id;

    @Schema(description = "Model Type(Memory/ASR/VAD/LLM/TTS)")
    private String modelType;

    @Schema(description = "Model code(如AliLLM、DoubaoTTS)")
    private String modelCode;

    @Schema(description = "Model name")
    private String modelName;

    @Schema(description = "default config status(0:no 1:yes)")
    private Integer isDefault;

    @Schema(description = "enabled status")
    private Integer isEnabled;

    @TableField(typeHandler = JacksonTypeHandler.class)
    @Schema(description = "model config(JSON format)")
    private JSONObject configJson;

    @Schema(description = "official docs url")
    private String docLink;

    @Schema(description = "Remarks")
    private String remark;

    @Schema(description = "Sort order")
    private Integer sort;

    @Schema(description = "Updater")
    @TableField(fill = FieldFill.UPDATE)
    private Long updater;

    @Schema(description = "Update date")
    @TableField(fill = FieldFill.UPDATE)
    private Date updateDate;

    @Schema(description = "Creator")
    @TableField(fill = FieldFill.INSERT)
    private Long creator;

    @Schema(description = "Creation date")
    @TableField(fill = FieldFill.INSERT)
    private Date createDate;
}
