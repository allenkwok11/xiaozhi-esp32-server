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

}




