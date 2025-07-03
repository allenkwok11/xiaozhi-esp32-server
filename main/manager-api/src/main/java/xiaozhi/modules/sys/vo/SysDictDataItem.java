package xiaozhi.modules.sys.vo;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 字典数据VO
 */
@Data
@Schema(description = "Dictionary data items")
public class SysDictDataItem implements Serializable {

    @Schema(description = "Dictionary label")
    private String name;

    @Schema(description = "Dictionary value")
    private String key;
}
