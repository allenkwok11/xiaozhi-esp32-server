package xiaozhi.modules.Timbre.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;


/**
 * 音色表数据DTO
 * @author zjy
 * @since 2025-3-21
 */
@Data
@Schema(description = "音色表信息")
public class TimbreDataDTO {

    @Schema(description = "语言")
    private String languages;

    @Schema(description = "音色名称")
    private String name;

    @Schema(description = "备注")
    private String remark;

    @Schema(description = "排序")
    private long sort;

    @Schema(description = "对应 TTS 模型主键")
    private String ttsModelId;

    @Schema(description = "音色编码")
    private String ttsVoice;

    @Schema(description = "音频播放地址")
    private String voiceDemo;
}