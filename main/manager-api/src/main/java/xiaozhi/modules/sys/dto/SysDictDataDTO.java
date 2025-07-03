package xiaozhi.modules.sys.dto;

import java.io.Serializable;
import java.util.Date;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Null;
import lombok.Data;
import xiaozhi.common.utils.DateUtils;
import xiaozhi.common.validator.group.AddGroup;
import xiaozhi.common.validator.group.DefaultGroup;
import xiaozhi.common.validator.group.UpdateGroup;

/**
 * 字典数据
 */
@Data
@Schema(description = "Dictionary Data")
public class SysDictDataDTO implements Serializable {

    @Schema(description = "id")
    @Null(message = "{id.null}", groups = AddGroup.class)
    @NotNull(message = "{id.require}", groups = UpdateGroup.class)
    private Long id;

    @Schema(description = "Dictionary Type ID")
    @NotNull(message = "{sysdict.type.require}", groups = DefaultGroup.class)
    private Long dictTypeId;

    @Schema(description = "Dictionary label")
    @NotBlank(message = "{sysdict.label.require}", groups = DefaultGroup.class)
    private String dictLabel;

    @Schema(description = "Dictionary value")
    private String dictValue;

    @Schema(description = "remarks")
    private String remark;

    @Schema(description = "sort order")
    @Min(value = 0, message = "{sort.number}", groups = DefaultGroup.class)
    private Integer sort;

    @Schema(description = "created date")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    @JsonFormat(pattern = DateUtils.DATE_TIME_PATTERN)
    private Date createDate;

    @Schema(description = "updated date")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    @JsonFormat(pattern = DateUtils.DATE_TIME_PATTERN)
    private Date updateDate;
}