package xiaozhi.modules.device.service;

import java.util.List;
import java.util.Map;

import xiaozhi.common.page.PageData;
import xiaozhi.modules.device.dto.DeviceHeaderDTO;
import xiaozhi.modules.device.dto.DeviceReportReqDTO;
import xiaozhi.modules.device.dto.DeviceReportRespDTO;
import xiaozhi.modules.device.entity.DeviceEntity;

public interface DeviceService {

    /**
     * 根据Mac地址获取设备信息
     */
    DeviceEntity getDeviceById(String macAddress);

    /**
     * 检查设备是否激活
     */
    DeviceReportRespDTO checkDeviceActive(String macAddress, String deviceId, String clientId,
            DeviceReportReqDTO deviceReport);

    /**
     * 绑定设备
     */
    DeviceEntity bindDevice(Long userId, DeviceHeaderDTO deviceHeader);

    /**
     * 获取用户设备列表
     */
    List<DeviceEntity> getUserDevices(Long userId);

    /**
     * 解绑设备
     */
    void unbindDevice(Long userId, Long deviceId);

    /**
     * 管理员设备列表
     */
    PageData<DeviceEntity> adminDeviceList(Map<String, Object> params);

    /**
     * 设备激活
     */
    Boolean deviceActivation(String activationCode);
}