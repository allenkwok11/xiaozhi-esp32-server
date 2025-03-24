package xiaozhi.modules.model.mapper;

import org.apache.ibatis.annotations.Mapper;
import xiaozhi.modules.model.domain.ModelConfig;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
* @author chenerlei
* @description 针对表【ai_model_config(模型配置表)】的数据库操作Mapper
* @createDate 2025-03-22 15:31:57
* @Entity xiaozhi.modules.model.domain.ModelConfig
*/
@Mapper
public interface ModelConfigMapper extends BaseMapper<ModelConfig> {

}




