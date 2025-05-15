package xiaozhi.modules.model.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.annotation.UpdateGroup;
import xiaozhi.common.page.PageData;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.model.dto.ModelProviderDTO;
import xiaozhi.modules.model.service.ModelProviderService;

@AllArgsConstructor
@RestController
@RequestMapping("/models/provider")
@Tag(name = "模型供应器")
public class ModelProviderController {

    private final ModelProviderService modelProviderService;

    @GetMapping
    @Operation(summary = "获取模型供应器列表")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<PageData<ModelProviderDTO>> getListPage(ModelProviderDTO modelProviderDTO,
                                                             @RequestParam(required = true, defaultValue = "0") String page,
                                                             @RequestParam(required = true, defaultValue = "10") String limit) {
        return new Result<PageData<ModelProviderDTO>>()
                .ok(modelProviderService.getListPage(modelProviderDTO, page, limit));
    }

    @PostMapping
    @Operation(summary = "获取模型供应器列表")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<ModelProviderDTO> add(@RequestBody @Validated ModelProviderDTO modelProviderDTO) {
        ModelProviderDTO resp = modelProviderService.add(modelProviderDTO);
        return new Result<ModelProviderDTO>().ok(resp);
    }

    @PutMapping
    @Operation(summary = "获取模型供应器列表")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<ModelProviderDTO> edit(@RequestBody @Validated(UpdateGroup.class) ModelProviderDTO modelProviderDTO) {
        ModelProviderDTO resp = modelProviderService.edit(modelProviderDTO);
        return new Result<ModelProviderDTO>().ok(resp);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "获取模型供应器列表")
    @RequiresPermissions("sys:role:superAdmin")
    public Result<Void> delete(@PathVariable String id) {
        modelProviderService.delete(id);
        return new Result<>();
    }

}
