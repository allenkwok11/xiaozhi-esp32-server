package xiaozhi.modules.model.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import xiaozhi.modules.model.domain.ModelProvider;
import xiaozhi.modules.model.service.ModelProviderService;
import xiaozhi.modules.model.mapper.ModelProviderMapper;
import org.springframework.stereotype.Service;

/**
* @author chenerlei
* @description 针对表【ai_model_provider(模型配置表)】的数据库操作Service实现
* @createDate 2025-03-24 18:24:13
*/
@Service
public class ModelProviderServiceImpl extends ServiceImpl<ModelProviderMapper, ModelProvider>
    implements ModelProviderService{

//    private final ModelProviderDao modelProviderDao;
//
//    @Override
//    public List<ModelProviderDTO> getListByModelType(String modelType) {
//
//        QueryWrapper<ModelProviderEntity> queryWrapper = new QueryWrapper<>();
//        queryWrapper.eq("model_type", StringUtils.isBlank(modelType) ? "" : modelType);
//        List<ModelProviderEntity> providerEntities = modelProviderDao.selectList(queryWrapper);
//        return ConvertUtils.sourceToTarget(providerEntities, ModelProviderDTO.class);
//    }
//
//    @Override
//    public ModelProviderDTO add(ModelProviderEntity modelProviderEntity) {
//        return null;
//    }
//
//    @Override
//    public ModelProviderDTO edit(ModelProviderEntity modelProviderEntity) {
//        return null;
//    }
//
//    @Override
//    public void delete() {
//
//    }
//
//    @Override
//    public List<ModelProviderDTO> getList(String modelType, String provideCode) {
//        QueryWrapper<ModelProviderEntity> queryWrapper = new QueryWrapper<>();
//        queryWrapper.eq("model_type", StringUtils.isBlank(modelType) ? "" : modelType);
//        queryWrapper.eq("provide_code", StringUtils.isBlank(provideCode) ? "" : provideCode);
//        List<ModelProviderEntity> providerEntities = modelProviderDao.selectList(queryWrapper);
//        return ConvertUtils.sourceToTarget(providerEntities, ModelProviderDTO.class);
//    }
//
//    @Override
//    public List<String> getFieldList(String modelType, String provideCode) {
//        return modelProviderDao.getFieldList(modelType, provideCode);
//    }
}




