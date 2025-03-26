package xiaozhi.modules.model.mapper;

import org.apache.ibatis.annotations.Mapper;
import xiaozhi.modules.model.domain.ModelProvider;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
* @author chenerlei
* @description 针对表【ai_model_provider(模型配置表)】的数据库操作Mapper
* @createDate 2025-03-24 18:24:13
* @Entity xiaozhi.modules.model.domain.ModelProvider
*/
@Mapper
public interface ModelProviderMapper extends BaseMapper<ModelProvider> {

}




