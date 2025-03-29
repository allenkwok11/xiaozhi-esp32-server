package xiaozhi.modules.device.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import xiaozhi.modules.device.domain.Device;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.device.mapper.DeviceMapper;
import org.springframework.stereotype.Service;

/**
* @author chenerlei
* @description 针对表【ai_device(设备信息表)】的数据库操作Service实现
* @createDate 2025-03-22 13:26:35
*/
@Service
public class DeviceServiceImpl extends ServiceImpl<DeviceMapper, Device>
    implements DeviceService{

}




