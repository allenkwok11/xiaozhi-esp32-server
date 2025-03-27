package xiaozhi.modules.model.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import xiaozhi.modules.model.domain.ModelConfig;
import xiaozhi.modules.model.service.ModelConfigService;
import xiaozhi.modules.model.mapper.ModelConfigMapper;
import org.springframework.stereotype.Service;

/**
* @author chenerlei
* @description 针对表【ai_model_config(模型配置表)】的数据库操作Service实现
* @createDate 2025-03-22 15:31:57
*/
@Service
public class ModelConfigServiceImpl extends ServiceImpl<ModelConfigMapper, ModelConfig>
    implements ModelConfigService{

//    private final ModelConfigDao modelConfigDao;
//    private final ModelProviderService modelProviderService;
//    private final TimbreService timbreService;
//
//    private static final Logger logger = LoggerFactory.getLogger(ModelConfigServiceImpl.class);
//
//    @Override
//    public List<String> getModelCodeList(String modelType, String modelName) {
//        return modelConfigDao.getModelCodeList(modelType, modelName);
//    }
//
//    @Override
//    public PageData<ModelConfigDTO> getPageList(String modelType, String modelName, Integer page, Integer limit) {
//        Map<String, Object> params = new HashMap<String, Object>();
//        params.put(Constant.PAGE, page);
//        params.put(Constant.LIMIT, limit);
//        IPage<ModelConfigEntity> modelConfigEntityIPage = modelConfigDao.selectPage(
//                getPage(params, "sort", true),
//                new QueryWrapper<ModelConfigEntity>()
//                        .eq("model_type", modelType)
//                        .like(StringUtils.isNotBlank(modelName), "model_name", modelName)
//        );
//        return getPageData(modelConfigEntityIPage, ModelConfigDTO.class);
//    }
//
//    @Override
//    public ModelConfigDTO add(String modelType, String provideCode, ModelConfigBodyDTO modelConfigBodyDTO) {
//        // 先验证有没有供应器
//        if (StringUtils.isBlank(modelType) || StringUtils.isBlank(provideCode)) {
//            throw new RenException("modelType和provideCode不能为空");
//        }
//        List<ModelProviderDTO> providerList = modelProviderService.getList(modelType, provideCode);
//        if (CollectionUtil.isEmpty(providerList)) {
//            throw new RenException("供应器不存在");
//        }
//
//        // 再保存供应器提供的模型
//        ModelConfigEntity modelConfigEntity = ConvertUtils.sourceToTarget(modelConfigBodyDTO, ModelConfigEntity.class);
//        modelConfigEntity.setModelType(modelType);
//        modelConfigDao.insert(modelConfigEntity);
//        return ConvertUtils.sourceToTarget(modelConfigEntity, ModelConfigDTO.class);
//    }
//
//    @Override
//    public ModelConfigDTO edit(String modelType, String provideCode, String id, ModelConfigBodyDTO modelConfigBodyDTO) {
//        // 先验证有没有供应器
//        if (StringUtils.isBlank(modelType) || StringUtils.isBlank(provideCode)) {
//            throw new RenException("modelType和provideCode不能为空");
//        }
//        List<ModelProviderDTO> providerList = modelProviderService.getList(modelType, provideCode);
//        if (CollectionUtil.isEmpty(providerList)) {
//            throw new RenException("供应器不存在");
//        }
//
//        // 再更新供应器提供的模型
//        ModelConfigEntity modelConfigEntity = ConvertUtils.sourceToTarget(modelConfigBodyDTO, ModelConfigEntity.class);
//        modelConfigEntity.setId(id);
//        modelConfigEntity.setModelType(modelType);
//        modelConfigDao.updateById(modelConfigEntity);
//        return ConvertUtils.sourceToTarget(modelConfigEntity, ModelConfigDTO.class);
//    }
//
//    @Override
//    public void delete(String modelType, String provideCode, String id) {
//        // 先验证有没有供应器
//        if (StringUtils.isBlank(modelType) || StringUtils.isBlank(provideCode)) {
//            throw new RenException("modelType和provideCode不能为空");
//        }
//        List<ModelProviderDTO> providerList = modelProviderService.getList(modelType, provideCode);
//        if (CollectionUtil.isEmpty(providerList)) {
//            throw new RenException("供应器不存在");
//        }
//
//        modelConfigDao.deleteById(Long.getLong(id));
//    }
//
//    @Override
//    public List<String> getVoiceList(String modelName, String voiceName) {
//        QueryWrapper<ModelConfigEntity> queryWrapper = new QueryWrapper<>();
//        queryWrapper.eq("model_name", StringUtils.isBlank(modelName) ? "" : modelName);
//        queryWrapper.eq("model_type", "TTS");
//        List<ModelConfigEntity> modelConfigEntities = modelConfigDao.selectList(queryWrapper);
//        if (CollectionUtil.isEmpty(modelConfigEntities)) {
//            logger.warn("没有找到模型配置信息");
//            return null;
//        }
//        ModelConfigEntity modelConfigEntity = modelConfigEntities.get(0);
//        String id = modelConfigEntity.getId();
//
//       return timbreService.getVoiceNames(id, voiceName);
//    }
}




