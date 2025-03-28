package xiaozhi.modules.device.service;

import xiaozhi.common.page.PageData;
import xiaozhi.modules.device.dto.DeviceBindDTO;
import xiaozhi.modules.device.entity.DeviceEntity;

import java.util.List;
import java.util.Map;

public interface DeviceService {
    void bindDevice(DeviceBindDTO dto);
    
    List<DeviceEntity> getUserDevices(Long userId);
    
    void unbindDevice(Long userId, Long deviceId);
    
    PageData<DeviceEntity> adminDeviceList(Map<String, Object> params);
}