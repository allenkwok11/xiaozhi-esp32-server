package xiaozhi.modules.model.service.impl;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.baomidou.mybatisplus.core.metadata.IPage;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;

import lombok.AllArgsConstructor;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.exception.RenException;
import xiaozhi.common.page.PageData;
import xiaozhi.common.service.impl.BaseServiceImpl;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.ConvertUtils;
import xiaozhi.modules.model.dao.ModelProviderDao;
import xiaozhi.modules.model.dto.ModelProviderDTO;
import xiaozhi.modules.model.entity.ModelProviderEntity;
import xiaozhi.modules.model.service.ModelProviderService;
import xiaozhi.modules.security.user.SecurityUser;

@Service
@AllArgsConstructor
public class ModelProviderServiceImpl extends BaseServiceImpl<ModelProviderDao, ModelProviderEntity>
        implements ModelProviderService {

    private final ModelProviderDao modelProviderDao;

    @Override
    public List<ModelProviderDTO> getListByModelType(String modelType) {

        QueryWrapper<ModelProviderEntity> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("model_type", StringUtils.isBlank(modelType) ? "" : modelType);
        List<ModelProviderEntity> providerEntities = modelProviderDao.selectList(queryWrapper);
        return ConvertUtils.sourceToTarget(providerEntities, ModelProviderDTO.class);
    }

    @Override
    public PageData<ModelProviderDTO> getListPage(ModelProviderDTO modelProviderEntity, String page, String limit) {

        Map<String, Object> params = new HashMap<String, Object>();
        params.put(Constant.PAGE, page);
        params.put(Constant.LIMIT, limit);

        IPage<ModelProviderEntity> pageParam = getPage(params, "model_type", true);

        QueryWrapper<ModelProviderEntity> wrapper = new QueryWrapper<ModelProviderEntity>();

        if (StringUtils.isNotBlank(modelProviderEntity.getModelType())) {
            wrapper.eq("model_type", modelProviderEntity.getModelType());
        }

        if (StringUtils.isNotBlank(modelProviderEntity.getName())) {
            wrapper.like("name", "%" + modelProviderEntity.getName() + "%");
        }
        return getPageData(modelProviderDao.selectPage(pageParam, wrapper), ModelProviderDTO.class);
    }

    @Override
    public ModelProviderDTO add(ModelProviderDTO modelProviderEntity) {
        UserDetail user = SecurityUser.getUser();
        modelProviderEntity.setCreator(user.getId());
        modelProviderEntity.setUpdater(user.getId());
        modelProviderEntity.setCreateDate(new Date());
        modelProviderEntity.setUpdateDate(new Date());
        if (modelProviderDao.insert(ConvertUtils.sourceToTarget(modelProviderEntity, ModelProviderEntity.class)) == 0) {
            throw new RenException("新增数据失败");
        }

        return ConvertUtils.sourceToTarget(modelProviderEntity, ModelProviderDTO.class);
    }

    @Override
    public ModelProviderDTO edit(ModelProviderDTO modelProviderEntity) {
        UserDetail user = SecurityUser.getUser();
        modelProviderEntity.setUpdater(user.getId());
        modelProviderEntity.setUpdateDate(new Date());
        if (modelProviderDao.updateById(ConvertUtils.sourceToTarget(modelProviderEntity, ModelProviderEntity.class)) == 0) {
            throw new RenException("修改数据失败");
        }
        return ConvertUtils.sourceToTarget(modelProviderEntity, ModelProviderDTO.class);
    }

    @Override
    public void delete(String id) {
        modelProviderDao.deleteById(id);
    }

    @Override
    public List<ModelProviderDTO> getList(String modelType, String providerCode) {
        QueryWrapper<ModelProviderEntity> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("model_type", StringUtils.isBlank(modelType) ? "" : modelType);
        queryWrapper.eq("provider_code", StringUtils.isBlank(providerCode) ? "" : providerCode);
        List<ModelProviderEntity> providerEntities = modelProviderDao.selectList(queryWrapper);
        return ConvertUtils.sourceToTarget(providerEntities, ModelProviderDTO.class);
    }
}
