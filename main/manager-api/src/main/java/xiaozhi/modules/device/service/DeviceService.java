package xiaozhi.modules.device.service;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.device.dto.DeviceHeaderDTO;
import xiaozhi.modules.device.entity.DeviceEntity;

import java.util.List;
import java.util.Map;

public interface DeviceService extends BaseService<DeviceEntity> {
    DeviceEntity bindDevice(Long userId, DeviceHeaderDTO deviceHeader);

    List<DeviceEntity> getUserDevices(Long userId);

    void unbindDevice(Long userId, Long deviceId);

    PageData<DeviceEntity> adminDeviceList(Map<String, Object> params);
}