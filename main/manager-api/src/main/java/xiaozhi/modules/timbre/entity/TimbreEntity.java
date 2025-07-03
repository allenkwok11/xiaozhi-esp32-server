package xiaozhi.modules.timbre.entity;

import java.util.Date;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 音色表实体类
 * 
 * @author zjy
 * @since 2025-3-21
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_tts_voice")
@Schema(description = "Timbre information")
public class TimbreEntity {

    @Schema(description = "ID")
    private String id;

    @Schema(description = "Language")
    private String languages;

    @Schema(description = "Timbre name")
    private String name;

    @Schema(description = "Remarks")
    private String remark;

    @Schema(description = "Sort order")
    private long sort;

    @Schema(description = "Associated TTS model primary key")
    private String ttsModelId;

    @Schema(description = "Timbre code")
    private String ttsVoice;

    @Schema(description = "Audio playback URL")
    private String voiceDemo;

    @Schema(description = "Updater")
    @TableField(fill = FieldFill.UPDATE)
    private Long updater;

    @Schema(description = "Update time")
    @TableField(fill = FieldFill.UPDATE)
    private Date updateDate;

    @Schema(description = "Creator")
    @TableField(fill = FieldFill.INSERT)
    private Long creator;

    @Schema(description = "Creation time")
    @TableField(fill = FieldFill.INSERT)
    private Date createDate;

}
