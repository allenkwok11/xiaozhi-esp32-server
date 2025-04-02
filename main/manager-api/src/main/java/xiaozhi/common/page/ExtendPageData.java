package xiaozhi.common.page;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 扩展的分页对象
 * @author zjy
 * @since 2025-4-2
 */
@Data
@Schema(description = "分页数据")
public class ExtendPageData<T> implements Serializable {
    @Schema(description = "总记录数")
    private int totalCount;

    @Schema(description = "页数")
    private int totalPage;

    @Schema(description = "列表数据")
    private List<T> list;

    /**
     * 分页
     *
     * @param list  列表数据
     * @param total 总记录数
     * @param page 页数
     */
    public ExtendPageData(List<T> list, long total, long page) {
        this.list = list;
        this.totalCount = (int) total;
        this.totalPage = (int) page;
    }
}