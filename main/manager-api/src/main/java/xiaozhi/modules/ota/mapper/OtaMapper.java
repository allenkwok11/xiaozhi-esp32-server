package xiaozhi.modules.ota.mapper;

import org.apache.ibatis.annotations.Mapper;
import xiaozhi.modules.ota.domain.Ota;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
* @author chenerlei
* @description 针对表【ai_ota(OTA升级信息表)】的数据库操作Mapper
* @createDate 2025-03-24 18:25:14
* @Entity xiaozhi.modules.ota.domain.Ota
*/
@Mapper
public interface OtaMapper extends BaseMapper<Ota> {

}




