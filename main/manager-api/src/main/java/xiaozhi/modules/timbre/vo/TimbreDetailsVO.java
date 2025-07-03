package xiaozhi.modules.timbre.vo;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 音色详情展示VO
 * 
 * @author zjy
 * @since 2025-3-21
 */
@Data
public class TimbreDetailsVO implements Serializable {

    @Schema(description = "Timbre ID")
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

}

