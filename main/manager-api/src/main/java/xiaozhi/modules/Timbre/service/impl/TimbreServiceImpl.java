package xiaozhi.modules.Timbre.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.page.PageData;
import xiaozhi.common.service.impl.BaseServiceImpl;
import xiaozhi.common.utils.ConvertUtils;
import xiaozhi.modules.Timbre.dao.TimbreDao;
import xiaozhi.modules.Timbre.dto.TimbreDataDTO;
import xiaozhi.modules.Timbre.dto.TimbrePageDTO;
import xiaozhi.modules.Timbre.service.TimbreService;
import xiaozhi.modules.Timbre.entity.TimbreEntity;
import xiaozhi.modules.Timbre.vo.TimbreDetailsVO;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * 音色的业务层的实现
 * @author zjy
 * @since 2025-3-21
 */
@Service
public class TimbreServiceImpl extends BaseServiceImpl<TimbreDao, TimbreEntity> implements TimbreService {


    @Override
    public PageData<TimbreDetailsVO> page(TimbrePageDTO dto) {
        Map<String, Object> params = new HashMap<String, Object>();
        params.put(Constant.PAGE, dto.getPage());
        params.put(Constant.LIMIT,dto.getLimit());
        IPage<TimbreEntity> page = baseDao.selectPage(
                getPage(params, "sort", true),
                //定义查询条件
                new QueryWrapper<TimbreEntity>()
                        //必须按照ttsID查找
                        .eq("tts_model_id",dto.getTtsModelId())
                        //如果有音色名字，按照音色名模糊查找
                        .like(StringUtils.isNotBlank(dto.getName()),"name",dto.getName())
        );

        return getPageData(page, TimbreDetailsVO.class);
    }

    @Override
    public TimbreDetailsVO get(Long timbreId) {
        TimbreEntity entity = baseDao.selectById(timbreId);
        return ConvertUtils.sourceToTarget(entity, TimbreDetailsVO.class);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void save(TimbreDataDTO dto) {
        isTtsModelId(dto.getTtsModelId());
        TimbreEntity timbreEntity = ConvertUtils.sourceToTarget(dto, TimbreEntity.class);
        baseDao.insert(timbreEntity);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void update(Long timbreId, TimbreDataDTO dto) {
        isTtsModelId(dto.getTtsModelId());
        TimbreEntity timbreEntity = ConvertUtils.sourceToTarget(dto, TimbreEntity.class);
        timbreEntity.setId(timbreId);
        baseDao.updateById(timbreEntity);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void delete(Long[] ids) {
        baseDao.deleteBatchIds(Arrays.asList(ids));
    }

    /**
     * 处理是不是tts模型的id
     */
    private void isTtsModelId(String ttsModelId){
        //等模型配置那边写好调用方法判断
    }
}