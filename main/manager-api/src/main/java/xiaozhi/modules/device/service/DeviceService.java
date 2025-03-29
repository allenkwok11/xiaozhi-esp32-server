package xiaozhi.modules.device.service;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.device.dto.DeviceHeaderDTO;
import xiaozhi.modules.device.dto.DeviceReportReqDTO;
import xiaozhi.modules.device.dto.DeviceReportRespDTO;
import xiaozhi.modules.device.entity.DeviceEntity;

import java.util.List;
import java.util.Map;

public interface DeviceService {

    /**
    * 根据Mac地址获取设备信息
    */
    DeviceEntity getDeviceById(String macAddress);

    DeviceReportRespDTO checkDeviceActive(String macAddress, String deviceId, String clientId, DeviceReportReqDTO deviceReport);

    DeviceEntity bindDevice(Long userId, DeviceHeaderDTO deviceHeader);

    List<DeviceEntity> getUserDevices(Long userId);

    void unbindDevice(Long userId, Long deviceId);

    PageData<DeviceEntity> adminDeviceList(Map<String, Object> params);

    Boolean deviceActivation(String activationCode);
}