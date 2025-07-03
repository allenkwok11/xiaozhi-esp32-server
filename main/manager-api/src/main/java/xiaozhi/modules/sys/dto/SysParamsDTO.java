package xiaozhi.modules.sys.dto;

import java.io.Serializable;
import java.util.Date;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Null;
import jakarta.validation.constraints.Pattern;
import lombok.Data;
import xiaozhi.common.utils.DateUtils;
import xiaozhi.common.validator.group.AddGroup;
import xiaozhi.common.validator.group.DefaultGroup;
import xiaozhi.common.validator.group.UpdateGroup;

/**
 * 参数管理
 */
@Data
@Schema(description = "Parameter Management")
public class SysParamsDTO implements Serializable {

    @Schema(description = "id")
    @Null(message = "{id.null}", groups = AddGroup.class)
    @NotNull(message = "{id.require}", groups = UpdateGroup.class)
    private Long id;

    @Schema(description = "Parameter code")
    @NotBlank(message = "{sysparams.paramcode.require}", groups = DefaultGroup.class)
    private String paramCode;

    @Schema(description = "Parameter value")
    @NotBlank(message = "{sysparams.paramvalue.require}", groups = DefaultGroup.class)
    private String paramValue;

    @Schema(description = "value type")
    @NotBlank(message = "{sysparams.valuetype.require}", groups = DefaultGroup.class)
    @Pattern(regexp = "^(string|number|boolean|array|json)$", message = "{sysparams.valuetype.pattern}", groups = DefaultGroup.class)
    private String valueType;

    @Schema(description = "remarks")
    private String remark;

    @Schema(description = "Created date")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    @JsonFormat(pattern = DateUtils.DATE_TIME_PATTERN)
    private Date createDate;

    @Schema(description = "updated date")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    @JsonFormat(pattern = DateUtils.DATE_TIME_PATTERN)
    private Date updateDate;

}
