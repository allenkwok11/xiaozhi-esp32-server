package xiaozhi.modules.Timbre.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.page.PageData;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.Timbre.dto.TimbreDataDTO;
import xiaozhi.modules.Timbre.dto.TimbrePageDTO;
import xiaozhi.modules.Timbre.service.TimbreService;
import xiaozhi.modules.Timbre.vo.TimbreDetailsVO;

/**
 * 音色控制层
 * @author zjy
 * @since 2025-3-21
 */
@AllArgsConstructor
@RestController
@RequestMapping("/ttsVoice")
@Tag(name = "音色管理")
public class TimbreController {
    private final TimbreService timbreService;

    @GetMapping
    @Operation(summary = "分页查找")
//    @RequiresPermissions("sys:role:normal")
    public Result<PageData<TimbreDetailsVO>> page(@ModelAttribute TimbrePageDTO dto) {
        PageData<TimbreDetailsVO> page = timbreService.page(dto);
        return new Result<PageData<TimbreDetailsVO>>().ok(page);
    }
    @PostMapping
    @Operation(summary = "音色保存")
//    @RequiresPermissions("sys:role:normal")
    public Result<Void> save(@RequestBody TimbreDataDTO dto) {
        timbreService.save(dto);
        return new Result<>();
    }
    @PutMapping("/{id}")
    @Operation(summary = "音色修改")
//    @RequiresPermissions("sys:role:normal")
    public Result<Void> update(@PathVariable Long id,@RequestBody TimbreDataDTO dto) {
        timbreService.update(id,dto);
        return new Result<>();
    }
    @DeleteMapping("/{id}")
    @Operation(summary = "音色删除")
//    @RequiresPermissions("sys:role:normal")
    public Result<Void> delete(@PathVariable Long id) {
        timbreService.delete(new Long[]{id});
        return new Result<>();
    }



}