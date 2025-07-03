package xiaozhi.common.page;

import java.io.Serializable;
import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 分页工具类
 * Copyright (c) 人人开源 All rights reserved.
 * Website: https://www.renren.io
 */
@Data
@Schema(description = "Paginated data")
public class PageData<T> implements Serializable {
    @Schema(description = "total record number")
    private int total;

    @Schema(description = "list data ")
    private List<T> list;

    /**
     * 分页
     *
     * @param list  列表数据
     * @param total 总记录数
     */
    public PageData(List<T> list, long total) {
        this.list = list;
        this.total = (int) total;
    }
}