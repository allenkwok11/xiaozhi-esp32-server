package xiaozhi.modules.timbre.controller;

import java.util.Map;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.Parameters;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.page.PageData;
import xiaozhi.common.utils.Result;
import xiaozhi.common.validator.ValidatorUtils;
import xiaozhi.modules.timbre.dto.TimbreDataDTO;
import xiaozhi.modules.timbre.dto.TimbrePageDTO;
import xiaozhi.modules.timbre.service.TimbreService;
import xiaozhi.modules.timbre.vo.TimbreDetailsVO;

/**
 * 音色控制层
 *
 * @author zjy
 * @since 2025-3-21
 */
@AllArgsConstructor
@RestController
@RequestMapping("/ttsVoice")
@Tag(name = "TTS Voice Management")
public class TimbreController {
    private final TimbreService timbreService;

    @GetMapping
    @Operation(summary = "Paginated search")
    @RequiresPermissions("sys:role:superAdmin")
    @Parameters({
            @Parameter(name = "ttsModelId", description = "mapp TTS model primary key", required = true),
            @Parameter(name = "name", description = "voice name"),
            @Parameter(name = Constant.PAGE, description = "current page, start from 1", required = true),
            @Parameter(name = Constant.LIMIT, description = "records per page", required = true),
    })
    public Result<PageData<TimbreDetailsVO>> page(
            @Parameter(hidden = true) @RequestParam Map<String, Object> params) {
        TimbrePageDTO dto = new TimbrePageDTO();
        dto.setTtsModelId((String) params.get("ttsModelId"));
        dto.setName((String) params.get("name"));
        dto.setLimit((String) params.get(Constant.LIMIT));
        dto.setPage((String) params.get(Constant.PAGE));

        ValidatorUtils.validateEntity(dto);
        PageData<TimbreDetailsVO> page = timbreService.page(dto);
        return new Result<PageData<TimbreDetailsVO>>().ok(page);
    }

    @PostMapping
    @Operation(summary = "save voice")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Void> save(@RequestBody TimbreDataDTO dto) {
        ValidatorUtils.validateEntity(dto);
        timbreService.save(dto);
        return new Result<>();
    }

    @PutMapping("/{id}")
    @Operation(summary = "edit voice")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Void> update(
            @PathVariable String id,
            @RequestBody TimbreDataDTO dto) {
        ValidatorUtils.validateEntity(dto);
        timbreService.update(id, dto);
        return new Result<>();
    }

    @PostMapping("/delete")
    @Operation(summary = "delete voice")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Void> delete(@RequestBody String[] ids) {
        timbreService.delete(ids);
        return new Result<>();
    }

}