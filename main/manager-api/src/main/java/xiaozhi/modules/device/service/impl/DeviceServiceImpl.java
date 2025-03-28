package xiaozhi.modules.device.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import org.springframework.stereotype.Service;
import xiaozhi.common.page.PageData;
import xiaozhi.common.service.impl.BaseServiceImpl;
import xiaozhi.common.utils.ConvertUtils;
import xiaozhi.modules.device.dao.DeviceDao;
import xiaozhi.modules.device.dto.DeviceBindDTO;
import xiaozhi.modules.device.entity.DeviceEntity;
import xiaozhi.modules.device.service.DeviceService;

import java.util.List;
import java.util.Map;

@Service
public class DeviceServiceImpl extends BaseServiceImpl<DeviceDao, DeviceEntity> implements DeviceService {
    @Override
    public void bindDevice(DeviceBindDTO dto) {
        DeviceEntity deviceEntity = ConvertUtils.sourceToTarget(dto, DeviceEntity.class);
        baseDao.insert(deviceEntity);
    }

    @Override
    public List<DeviceEntity> getUserDevices(Long userId) {
        QueryWrapper<DeviceEntity> wrapper = new QueryWrapper<>();
        wrapper.eq("user_id", userId);
        return baseDao.selectList(wrapper);
    }

    @Override
    public void unbindDevice(Long userId, Long deviceId) {
        baseDao.deleteById(deviceId);
    }

    @Override
    public PageData<DeviceEntity> adminDeviceList(Map<String, Object> params) {
        IPage<DeviceEntity> page = baseDao.selectPage(
                getPage(params, "sort", true),
                new QueryWrapper<>()
        );
        return new PageData<>(page.getRecords(), page.getTotal());
    }

}