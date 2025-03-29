package xiaozhi.modules.device.mapper;

import org.apache.ibatis.annotations.Mapper;
import xiaozhi.modules.device.domain.Device;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
* @author chenerlei
* @description 针对表【ai_device(设备信息表)】的数据库操作Mapper
* @createDate 2025-03-22 13:26:35
* @Entity xiaozhi.modules.device.domain.Device
*/
@Mapper
public interface DeviceMapper extends BaseMapper<Device> {

}




